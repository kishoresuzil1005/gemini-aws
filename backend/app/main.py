import time
import uuid
import threading
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import is_aws_configured, AWS_DEFAULT_REGION
from .database import (
    init_db, get_db, CloudAccountDB, DiscoveryResourceDB, 
    SavedMigrationDB, CloudIncidentDB, BackgroundJobDB
)
from .aws_scanner import (
    scan_aws_resources, heal_security_group_ssh, heal_s3_bucket_encryption
)

app = FastAPI(
    title="CloudOps SRE Intelligence Center",
    description="FastAPI Backend for programmatically scanning multi-cloud systems & executing DevSecOps repairs.",
    version="1.0.0"
)

# Enable CORS so our local Android Emulators (10.0.2.2 or real devices) can speak to our services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas ---
class CloudAccountSchema(BaseModel):
    id: Optional[int] = None
    provider: str
    name: str
    credentialsHint: str
    region: str

    class Config:
        from_attributes = True

class DiscoveryResourceSchema(BaseModel):
    id: str
    provider: str
    type: str
    name: str
    configurationHint: str
    costEstimate: float
    dependenciesString: str

    class Config:
        from_attributes = True

class SavedMigrationSchema(BaseModel):
    id: Optional[int] = None
    title: str
    sourceCloud: str
    targetCloud: str
    servicesMigrated: str
    terraformCode: str

    class Config:
        from_attributes = True

class CloudIncidentSchema(BaseModel):
    id: str
    title: str
    severity: str
    resourceId: str
    description: str
    status: str
    timestamp: str

    class Config:
        from_attributes = True

class BackgroundJobSchema(BaseModel):
    id: str
    name: str
    progress: float
    status: str
    timestamp: str

    class Config:
        from_attributes = True


# --- Startup Event to SeedTest Data ---
@app.on_event("startup")
def startup_event():
    init_db()
    db = next(get_db())
    
    # 1. Seed accounts if table is empty
    if db.query(CloudAccountDB).count() == 0:
        db.add_all([
            CloudAccountDB(
                provider="AWS",
                name="AWS Corporate Main",
                credentials_hint="AWS_ACCESS_KEY_ID & SECRET configured in env",
                region=AWS_DEFAULT_REGION
            ),
            CloudAccountDB(
                provider="Azure",
                name="Azure Corporate Sandbox",
                credentials_hint="Tenant ID: 9fcd-1234-58bc-fa39",
                region="eastus"
            )
        ])
    
    # 2. Seed baseline mock resources if empty
    if db.query(DiscoveryResourceDB).count() == 0:
        db.add_all([
            DiscoveryResourceDB(
                id="vpc-09ab02c",
                provider="AWS",
                type="VPC",
                name="Main-Corporate-Net",
                configuration_hint="CIDR: 10.0.0.0/16 | Subnets: 4 Active",
                cost_estimate=0.0,
                dependencies_string="app-web-servers,rds-primary"
            ),
            DiscoveryResourceDB(
                id="app-web-servers",
                provider="AWS",
                type="EC2",
                name="FastAPI-Web-Cluster",
                configuration_hint="Ubuntu 22.04 LTS | Instance: m5.large | AutoScale: 2-8",
                cost_estimate=152.40,
                dependencies_string="rds-primary,sqs-event-queue"
            ),
            DiscoveryResourceDB(
                id="rds-primary",
                provider="AWS",
                type="RDS",
                name="PostgreSQL-MasterDB",
                configuration_hint="Engine: PostgreSQL 14.2 | Class: db.m5.xlarge | Multi-AZ",
                cost_estimate=340.00,
                dependencies_string=""
            ),
            DiscoveryResourceDB(
                id="s3-corporate-archive",
                provider="AWS",
                type="S3",
                name="s3-corporate-archive-992",
                configuration_hint="Storage size: 14.2TB | Encryption: None | Lock: Enabled",
                cost_estimate=820.00,
                dependencies_string=""
            ),
            DiscoveryResourceDB(
                id="lambda-processor",
                provider="AWS",
                type="Lambda",
                name="Telemetry-Sanitize-Worker",
                configuration_hint="Python 3.10 | Timeout: 120s | Memory: 512MB",
                cost_estimate=15.00,
                dependencies_string="sqs-event-queue"
            ),
            DiscoveryResourceDB(
                id="sqs-event-queue",
                provider="AWS",
                type="SQS",
                name="billing-events-queue.fifo",
                configuration_hint="Type: FIFO | Retention: 4 Days",
                cost_estimate=18.20,
                dependencies_string="sns-billing-topic"
            )
        ])

    # 3. Seed baseline incidents if empty
    if db.query(CloudIncidentDB).count() == 0:
        timestr = time.strftime("%H:%M:%S")
        db.add_all([
            CloudIncidentDB(
                id="inc-01",
                title="Critical CPU Spike on Web clusters",
                severity="CRITICAL",
                resource_id="app-web-servers",
                description="FastAPI web server nodes ('app-web-servers') are experiencing an anomalous memory leak and CPU spike. CPU utilization is reaching 98.4%. Scaler limit warning.",
                status="ACTIVE",
                timestamp=timestr
            ),
            CloudIncidentDB(
                id="inc-02",
                title="Wildcard SSH Security Group Open",
                severity="WARNING",
                resource_id="vpc-09ab02c",
                description="Port 22 SSH ingress open to entire internet ('0.0.0.0/0') within 'Main-Corporate-Net' resource group 'sg-web-public'.",
                status="ACTIVE",
                timestamp=timestr
            ),
            CloudIncidentDB(
                id="inc-03",
                title="Storage Blob Archive Unencrypted",
                severity="WARNING",
                resource_id="s3-corporate-archive",
                description="Audit scans found that AWS object bucket 's3-corporate-archive-992' contains 14.2TB of archive logs without default KMS encryption tags.",
                status="ACTIVE",
                timestamp=timestr
            )
        ])

    db.commit()
    db.close()


# --- Account API Endpoints ---

@app.get("/api/accounts", response_model=List[CloudAccountSchema])
def get_accounts(db: Session = Depends(get_db)):
    accts = db.query(CloudAccountDB).order_by(CloudAccountDB.created_at.desc()).all()
    # map to camelcase output schema safely
    return [
        CloudAccountSchema(
            id=a.id,
            provider=a.provider,
            name=a.name,
            credentialsHint=a.credentials_hint or "",
            region=a.region
        ) for a in accts
    ]

@app.post("/api/accounts", response_model=CloudAccountSchema)
def add_account(account: CloudAccountSchema, db: Session = Depends(get_db)):
    db_acct = CloudAccountDB(
        provider=account.provider,
        name=account.name,
        credentials_hint=account.credentialsHint,
        region=account.region
    )
    db.add(db_acct)
    db.commit()
    db.refresh(db_acct)
    return CloudAccountSchema(
        id=db_acct.id,
        provider=db_acct.provider,
        name=db_acct.name,
        credentialsHint=db_acct.credentials_hint or "",
        region=db_acct.region
    )

@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_acct = db.query(CloudAccountDB).filter(CloudAccountDB.id == account_id).first()
    if not db_acct:
        raise HTTPException(status_code=404, detail="Account not found.")
    db.delete(db_acct)
    db.commit()
    return {"status": "SUCCESS", "message": f"Successfully deleted cloud account: {account_id}"}


# --- Resource Discovery API Endpoints ---

@app.get("/api/resources", response_model=List[DiscoveryResourceSchema])
def get_resources(db: Session = Depends(get_db)):
    resources = db.query(DiscoveryResourceDB).all()
    return [
        DiscoveryResourceSchema(
            id=r.id,
            provider=r.provider,
            type=r.type,
            name=r.name,
            configurationHint=r.configuration_hint or "",
            costEstimate=r.cost_estimate,
            dependenciesString=r.dependencies_string or ""
        ) for r in resources
    ]


# --- Incident & Healing API Endpoints ---

@app.get("/api/incidents", response_model=List[CloudIncidentSchema])
def get_incidents(db: Session = Depends(get_db)):
    # Merge and query incidents. We check if there are real-world credentials to do a hot sync!
    incidents = db.query(CloudIncidentDB).all()
    
    # Check if we should inject real AWS scanned issues as well
    if is_aws_configured():
        _, aws_incidents = scan_aws_resources()
        # Merge those not already stored or just return dynamically
        stored_ids = {i.id for i in incidents}
        for item in aws_incidents:
            if item["id"] not in stored_ids:
                timestr = time.strftime("%H:%M:%S")
                new_inc = CloudIncidentDB(
                    id=item["id"],
                    title=item["title"],
                    severity=item["severity"],
                    resource_id=item["resourceId"],
                    description=item["description"],
                    status=item["status"],
                    timestamp=timestr
                )
                db.add(new_inc)
                db.commit()
                incidents.append(new_inc)

    return [
        CloudIncidentSchema(
            id=i.id,
            title=i.title,
            severity=i.severity,
            resourceId=i.resource_id,
            description=i.description,
            status=i.status,
            timestamp=i.timestamp
        ) for i in incidents
    ]

@app.post("/api/incidents/self-heal/{incident_id}")
def self_heal_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(CloudIncidentDB).filter(CloudIncidentDB.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found.")
    
    if inc.status != "ACTIVE":
        return {"status": "SUCCESS", "message": f"Incident was already resolved or is in a peaceful state.", "logs": []}

    inc.status = "HEALING"
    db.commit()

    logs = []
    # Real programmatic mitigation if credentials exist
    success = False
    message = ""
    
    if incident_id == "inc-02" or incident_id.startswith("aws-sg-"):
        success, message = heal_security_group_ssh(inc.resource_id)
        logs.append(message)
    elif incident_id == "inc-03" or incident_id.startswith("aws-s3-unencrypted-"):
        success, message = heal_s3_bucket_encryption(inc.resource_id)
        logs.append(message)
    else:
        # Default mock simulation logs
        success = True
        message = "Successfully executed local automation routine to mitigate server spike load."
        logs.append(message)

    if success:
        inc.status = "RESOLVED"
    else:
        inc.status = "ACTIVE" # restore status on failure
        logs.append("Healer: Reverting and reporting exception details to dashboard log streams.")

    db.commit()

    return {
        "status": "SUCCESS" if success else "FAILED",
        "message": message,
        "incidentStatus": inc.status,
        "logs": logs
    }

@app.post("/api/incidents/reset")
def reset_incidents(db: Session = Depends(get_db)):
    db.query(CloudIncidentDB).delete()
    db.commit()
    
    timestr = time.strftime("%H:%M:%S")
    db.add_all([
        CloudIncidentDB(
            id="inc-01",
            title="Critical CPU Spike on Web clusters",
            severity="CRITICAL",
            resource_id="app-web-servers",
            description="FastAPI web server nodes ('app-web-servers') are experiencing an anomalous memory leak and CPU spike. CPU utilization is reaching 98.4%. Scaler limit warning.",
            status="ACTIVE",
            timestamp=timestr
        ),
        CloudIncidentDB(
            id="inc-02",
            title="Wildcard SSH Security Group Open",
            severity="WARNING",
            resource_id="vpc-09ab02c",
            description="Port 22 SSH ingress open to entire internet ('0.0.0.0/0') within 'Main-Corporate-Net' resource group 'sg-web-public'.",
            status="ACTIVE",
            timestamp=timestr
        ),
        CloudIncidentDB(
            id="inc-03",
            title="Storage Blob Archive Unencrypted",
            severity="WARNING",
            resource_id="s3-corporate-archive",
            description="Audit scans found that AWS object bucket 's3-corporate-archive-992' contains 14.2TB of archive logs without default KMS encryption tags.",
            status="ACTIVE",
            timestamp=timestr
        )
    ])
    db.commit()
    return {"status": "SUCCESS", "message": "Baseline SRE incident records reconstituted."}


# --- Background Job / Discovery Scan Multi-thread Worker ---

def run_discovery_worker(job_id: str, db_session_factory, provider: str = "AWS"):
    db = db_session_factory()
    job = db.query(BackgroundJobDB).filter(BackgroundJobDB.id == job_id).first()
    if not job:
        db.close()
        return

    try:
        # Update progress phase 1
        job.status = "RUNNING"
        job.progress = 0.1
        db.commit()
        time.sleep(1.0)

        # Retrieve direct live resource inventory from AWS if credentials set
        scanned_resources = []
        is_live = False
        if is_aws_configured() and provider == "AWS":
            job.progress = 0.4
            db.commit()
            scanned_resources, _ = scan_aws_resources()
            is_live = True
            time.sleep(1.0)
        
        job.progress = 0.7
        db.commit()

        if is_live and scanned_resources:
            # Overwrite database with real discovered resources
            db.query(DiscoveryResourceDB).delete()
            for res in scanned_resources:
                db.add(DiscoveryResourceDB(
                    id=res["id"],
                    provider=res["provider"],
                    type=res["type"],
                    name=res["name"],
                    configuration_hint=res["configurationHint"],
                    cost_estimate=res["costEstimate"],
                    dependencies_string=res["dependenciesString"]
                ))
            db.commit()
        else:
            # In mock mode, we make sure the seeded resources remain populated
            pass
        
        job.progress = 1.0
        job.status = "COMPLETED"
        db.commit()
    except Exception as e:
        job.status = "FAILED"
        db.commit()
    finally:
        db.close()


@app.post("/api/discover", response_model=BackgroundJobSchema)
def trigger_discovery(background_tasks: BackgroundTasks, provider: str = "AWS", db: Session = Depends(get_db)):
    job_id = f"job-{uuid.uuid4().hex[:6]}"
    timestr = time.strftime("%H:%M:%S")
    
    # Store dynamic job structure
    db_job = BackgroundJobDB(
        id=job_id,
        name=f"Multi-Cloud Assets Sweeper (Cluster: {provider})",
        progress=0.0,
        status="QUEUED",
        timestamp=timestr
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Launch threaded daemon to scan AWS or simulate scanning without blocking FastAPI threads
    threading.Thread(target=run_discovery_worker, args=(job_id, SessionLocal, provider)).start()

    return BackgroundJobSchema(
        id=db_job.id,
        name=db_job.name,
        progress=db_job.progress,
        status=db_job.status,
        timestamp=db_job.timestamp
    )

@app.get("/api/jobs", response_model=List[BackgroundJobSchema])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(BackgroundJobDB).order_by(BackgroundJobDB.timestamp.desc()).all()
    return [
        BackgroundJobSchema(
            id=j.id,
            name=j.name,
            progress=j.progress,
            status=j.status,
            timestamp=j.timestamp
        ) for j in jobs
    ]

@app.get("/api/jobs/{job_id}", response_model=BackgroundJobSchema)
def get_job_details(job_id: str, db: Session = Depends(get_db)):
    job = db.query(BackgroundJobDB).filter(BackgroundJobDB.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Active SRE job track not found.")
    return BackgroundJobSchema(
        id=job.id,
        name=job.name,
        progress=job.progress,
        status=job.status,
        timestamp=job.timestamp
    )


# --- HCL Migrations API ---

@app.get("/api/migrations", response_model=List[SavedMigrationSchema])
def list_migrations(db: Session = Depends(get_db)):
    migrations = db.query(SavedMigrationDB).order_by(SavedMigrationDB.created_at.desc()).all()
    return [
        SavedMigrationSchema(
            id=m.id,
            title=m.title,
            sourceCloud=m.source_cloud,
            targetCloud=m.target_cloud,
            servicesMigrated=m.services_migrated,
            terraformCode=m.terraform_code
        ) for m in migrations
    ]

@app.post("/api/migrations", response_model=SavedMigrationSchema)
def save_migration(item: SavedMigrationSchema, db: Session = Depends(get_db)):
    db_mig = SavedMigrationDB(
        title=item.title,
        source_cloud=item.sourceCloud,
        target_cloud=item.targetCloud,
        services_migrated=item.servicesMigrated,
        terraform_code=item.terraformCode
    )
    db.add(db_mig)
    db.commit()
    db.refresh(db_mig)
    return SavedMigrationSchema(
        id=db_mig.id,
        title=db_mig.title,
        sourceCloud=db_mig.source_cloud,
        targetCloud=db_mig.target_cloud,
        servicesMigrated=db_mig.services_migrated,
        terraformCode=db_mig.terraform_code
    )

@app.delete("/api/migrations/{migration_id}")
def delete_migration(migration_id: int, db: Session = Depends(get_db)):
    db_mig = db.query(SavedMigrationDB).filter(SavedMigrationDB.id == migration_id).first()
    if not db_mig:
        raise HTTPException(status_code=404, detail="Compiled template reference not found.")
    db.delete(db_mig)
    db.commit()
    return {"status": "SUCCESS"}
