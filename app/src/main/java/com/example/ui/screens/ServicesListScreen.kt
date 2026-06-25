package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.CloudScreen
import com.example.ui.CloudViewModel
import com.example.ui.theme.*
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import coil.compose.AsyncImage
import coil.request.ImageRequest

data class ServiceItem(
    val title: String,
    val description: String,
    val icon: ImageVector,
    val screen: CloudScreen,
    val accentColor: Color,
    val tag: String,
    val isCoreSre: Boolean = false
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ServicesListScreen(
    isDarkTheme: Boolean,
    viewModel: CloudViewModel,
    onNavigateToScreen: (CloudScreen) -> Unit,
    modifier: Modifier = Modifier
) {
    val selectedRegion by viewModel.selectedRegion.collectAsState()
    val awsLogs by viewModel.awsLogs.collectAsState()
    val scope = rememberCoroutineScope()
    val context = LocalContext.current

    val assetMap = remember {
        val map = mutableMapOf<String, String>()
        val dirs = listOf("Analytics", "Application Integration", "Artificial Intelligence", "Business Applications", "Cloud Financial Management", "Customer Enablement", "Databases", "Developer Tools", "Front End Web Mobile", "Internet of Things", "Management Tools", "Media Services", "Migration Modernization", "Networking Content Delivery", "Security Identity", "Storage", "compute")
        dirs.forEach { dir ->
            try {
                context.assets.list(dir)?.forEach { file ->
                    val plainKey = file.removeSuffix(".jpg").removeSuffix(".svg").replace("-", "").lowercase()
                    map[plainKey] = "$dir/$file"
                }
            } catch (e: Exception) {}
        }
        map
    }

    var searchQuery by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf("All") }

    // Diagnostic/Log States
    var selectedServiceForDiagnostics by remember { mutableStateOf<ServiceItem?>(null) }
    var logTerminalLines by remember { mutableStateOf<List<String>>(emptyList()) }
    var activeDiagnosticsJob by remember { mutableStateOf<Job?>(null) }
    var isScanning by remember { mutableStateOf(false) }

    // Core SRE services definition
    val coreSreServices = remember {
        listOf(
            ServiceItem(
                title = "SRE Plane",
                description = "Visualize live traffic flow, service nodes, and active dependency mappings on a multi-tier topological graph.",
                icon = Icons.Default.Hub,
                screen = CloudScreen.SRE,
                accentColor = BentoPurplePrimary,
                tag = "sre",
                isCoreSre = true
            ),
            ServiceItem(
                title = "HCL Migrate",
                description = "Automatically generate complete, compliant HashiCorp Terraform (.tf) SRE configuration templates matching live cloud scans.",
                icon = Icons.Default.Code,
                screen = CloudScreen.HCL,
                accentColor = GCPColor,
                tag = "hcl",
                isCoreSre = true
            ),
            ServiceItem(
                title = "AI Architect",
                description = "Deploy the SRE chat assistant powered by Gemini-2.5-Flash to security inspect, audit IAM, and optimize infrastructure.",
                icon = Icons.Default.Chat,
                screen = CloudScreen.GEMINI,
                accentColor = NebulaPurple,
                tag = "gemini",
                isCoreSre = true
            ),
            ServiceItem(
                title = "Cloud Connectors",
                description = "Manage multicloud federated credentials, database schemas, and trigger instant regional scans.",
                icon = Icons.Default.Cloud,
                screen = CloudScreen.CLOUD,
                accentColor = AzureColor,
                tag = "cloud",
                isCoreSre = true
            ),
            ServiceItem(
                title = "CloudShell Terminal",
                description = "Open an interactive web command CLI console to query and configure cloud resource variables in real time.",
                icon = Icons.Default.Terminal,
                screen = CloudScreen.CLOUDSHELL,
                accentColor = TerminalGreen,
                tag = "shell",
                isCoreSre = true
            ),
            ServiceItem(
                title = "Autonomous Diagnosis",
                description = "Deploy the AI Doctor engine to detect, diagnose, and run autonomous self-healing loops on cloud-critical telemetry alerts.",
                icon = Icons.Default.SmartToy,
                screen = CloudScreen.AI,
                accentColor = BentoAccentRed,
                tag = "ai",
                isCoreSre = true
            ),
            ServiceItem(
                title = "AWS Service Call Logs",
                description = "Inspect real-time unblended API request telemetry, timestamps, status values, and parameters for all active boto3/SDK calls.",
                icon = Icons.Default.Receipt,
                screen = CloudScreen.SERVICES_LIST,
                accentColor = Color(0xFFFF9900),
                tag = "aws_logs",
                isCoreSre = true
            )
        )
    }

    // Standard AWS console reference services (90+ services from the user screenshots!)
    val standardAwsServices = remember {
        listOf(
            ServiceItem("AWS Amplify", "AWS Amplify offers web hosting and app backend services for fullstack developers.", Icons.Default.Cloud, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "amplify"),
            ServiceItem("API Gateway", "Build, Deploy and Manage APIs", Icons.Default.Router, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "api_gateway"),
            ServiceItem("AWS App Runner", "Build and run production web applications at scale", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "app_runner"),
            ServiceItem("AWS Artifact", "Security compliance reports and agreements", Icons.Default.Info, CloudScreen.SERVICES_LIST, Color(0xFF49454F), "artifact"),
            ServiceItem("Athena", "Serverless interactive analytics service", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "athena"),
            ServiceItem("Aurora and RDS", "Managed Relational Database Service", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "rds"),
            ServiceItem("AWS Backup", "AWS Backup centrally manages and automates backups across AWS services", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "backup"),
            ServiceItem("Batch", "Fully managed batch processing at any scale", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "batch"),
            ServiceItem("Amazon Bedrock", "The easiest way to build and scale generative AI applications with foundation models (FMs).", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "bedrock"),
            ServiceItem("Amazon Bedrock AgentCore", "Deploy and operate highly effective agents securely, at scale using any framework and model.", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "bedrock_agent"),
            ServiceItem("Billing and Cost Management", "View and pay bills, analyze and govern your spending, and optimize your costs", Icons.Default.Info, CloudScreen.SERVICES_LIST, Color(0xFF49454F), "billing"),
            ServiceItem("Certificate Manager", "Provision, Manage, and Deploy SSL/TLS Certificates", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "acm"),
            ServiceItem("Cloud9", "A Cloud IDE for Writing, Running, and Debugging Code", Icons.Default.Code, CloudScreen.SERVICES_LIST, Color(0xFF6750A4), "cloud9"),
            ServiceItem("CloudFormation", "Create and Manage Resources with Templates", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "cloudformation"),
            ServiceItem("CloudFront", "Global Content Delivery Network", Icons.Default.Router, CloudScreen.SERVICES_LIST, Color(0xFF1B5E20), "cloudfront"),
            ServiceItem("CloudShell", "A browser-based shell with AWS CLI access from the AWS Management Console", Icons.Default.Terminal, CloudScreen.SERVICES_LIST, Color(0xFF6750A4), "cloudshell"),
            ServiceItem("CloudTrail", "Track User Activity and API Usage", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "cloudtrail"),
            ServiceItem("CloudWatch", "Monitor Resources and Applications", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "cloudwatch"),
            ServiceItem("CodeBuild", "Build and Test Code", Icons.Default.Code, CloudScreen.SERVICES_LIST, Color(0xFF6750A4), "codebuild"),
            ServiceItem("CodeCommit", "Store Code in Private Git Repositories", Icons.Default.Code, CloudScreen.SERVICES_LIST, Color(0xFF6750A4), "codecommit"),
            ServiceItem("CodeDeploy", "Automate Code Deployments", Icons.Default.Code, CloudScreen.SERVICES_LIST, Color(0xFF6750A4), "codedeploy"),
            ServiceItem("CodePipeline", "Release Software using Continuous Delivery", Icons.Default.Code, CloudScreen.SERVICES_LIST, Color(0xFF6750A4), "codepipeline"),
            ServiceItem("Cognito", "Consumer Identity Management and AWS Credentials for Federated Identities", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "cognito"),
            ServiceItem("Control Tower", "The easiest way to set up and govern a secure, compliant multi-account environment", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "control_tower"),
            ServiceItem("AWS Deadline Cloud", "Simplified render management", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "deadline"),
            ServiceItem("Direct Connect", "Dedicated Network Connection to AWS", Icons.Default.Router, CloudScreen.SERVICES_LIST, Color(0xFF1B5E20), "direct_connect"),
            ServiceItem("Directory Service", "Host and Manage Active Directory", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "directory_service"),
            ServiceItem("Amazon DocumentDB", "Fully-managed MongoDB-compatible database service", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "documentdb"),
            ServiceItem("DynamoDB", "Managed NoSQL Database", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "dynamodb"),
            ServiceItem("EC2", "Virtual Servers in the Cloud", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "ec2"),
            ServiceItem("EC2 Image Builder", "A managed service to automate build, customize and deploy OS images", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "ec2_image_builder"),
            ServiceItem("Elastic Beanstalk", "Run and Manage Web Apps", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "beanstalk"),
            ServiceItem("Elastic Container Registry", "Fully-managed Docker container registry : Share and deploy container software, publicly or privately", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "ecr"),
            ServiceItem("Elastic Container Service", "Highly secure, reliable, and scalable way to run containers", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "ecs"),
            ServiceItem("AWS Elastic Disaster Recovery", "Scalable, cost-effective application recovery to AWS", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "disaster_recovery"),
            ServiceItem("Elastic Kubernetes Service", "The most trusted way to start, run, and scale Kubernetes", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "eks"),
            ServiceItem("ElasticCache", "In-Memory Cache", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "elasticache"),
            ServiceItem("EMR", "Managed Hadoop Framework", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "emr"),
            ServiceItem("Amazon EventBridge", "Serverless service for building event-driven applications", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "eventbridge"),
            ServiceItem("FSx", "Fully managed third-party file systems optimized for a variety of workloads", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "fsx"),
            ServiceItem("AWS Glue", "AWS Glue is a serverless data integration service.", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "glue"),
            ServiceItem("GuardDuty", "Intelligent Threat Detection to Protect Your AWS Accounts and Workloads", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "guardduty"),
            ServiceItem("AWS Health Dashboard", "Personalized view of AWS service health.", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "health_dashboard"),
            ServiceItem("IAM", "Manage access to AWS resources", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "iam"),
            ServiceItem("IAM Identity Center", "Manage workforce user access to multiple AWS accounts and cloud applications", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "iam_identity_center"),
            ServiceItem("Amazon Inspector", "Continual vulnerability management at scale", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "inspector"),
            ServiceItem("IoT Core", "Connect Devices to the Cloud", Icons.Default.Router, CloudScreen.SERVICES_LIST, Color(0xFF1B5E20), "iot_core"),
            ServiceItem("Key Management Service", "Securely Generate and Manage AWS Encryption Keys", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "kms"),
            ServiceItem("Kinesis", "Work with Real-Time Streaming Data", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "kinesis"),
            ServiceItem("Kiro", "Build applications faster, and spend less time solving software development problems", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "kiro"),
            ServiceItem("AWS Lake Formation", "AWS Lake Formation makes it easy to set up a secure data lake", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "lake_formation"),
            ServiceItem("Lambda", "Run code without thinking about servers", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "lambda"),
            ServiceItem("Lightsail", "Launch and Manage Virtual Private Servers", Icons.Default.Memory, CloudScreen.SERVICES_LIST, Color(0xFFFF9900), "lightsail"),
            ServiceItem("Managed Apache Airflow", "Run Apache Airflow without provisioning or managing servers.", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "airflow"),
            ServiceItem("MediaConnect", "Reliable, secure, and flexible transport for live video", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "mediaconnect"),
            ServiceItem("MediaLive", "Convert video inputs into live outputs for broadcast and streaming delivery", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "medialive"),
            ServiceItem("Amazon MQ", "Managed message broker service for Apache ActiveMQ and RabbitMQ", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "mq"),
            ServiceItem("MSK", "Fully managed, highly available, and secure service for Apache Kafka", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "msk"),
            ServiceItem("Amazon OpenSearch Service", "Run open-source OpenSearch or Elasticsearch using Managed Clusters or Serverless deployments.", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "opensearch"),
            ServiceItem("AWS Organizations", "Central governance and management across AWS accounts.", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "organizations"),
            ServiceItem("Amazon Personalize", "Amazon Personalize helps you easily add real-time recommendations to your apps", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "personalize"),
            ServiceItem("Amazon Polly", "Turn Text into Lifelike Speech", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "polly"),
            ServiceItem("AWS Private Certificate Authority", "Managed private certificate authority service", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "private_ca"),
            ServiceItem("Redshift", "Fast, Serverless, and cost effective SQL analytics and data warehousing", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "redshift"),
            ServiceItem("AWS Resilience Hub", "AWS Resilience Hub provides a central place to define, validate, and track the resiliency of applications on AWS.", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "resilience_hub"),
            ServiceItem("Resource Access Manager", "Share AWS resources with other accounts or AWS Organizations", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "ram"),
            ServiceItem("AWS Resource Explorer", "Easily search for and discover relevant resources across AWS", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "resource_explorer"),
            ServiceItem("Resource Groups & Tag Editor", "AWS Resource Groups Lets You Search and Group AWS Resources", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "resource_groups"),
            ServiceItem("Route 53", "Scalable DNS and Domain Name Registration", Icons.Default.Router, CloudScreen.SERVICES_LIST, Color(0xFF1B5E20), "route53"),
            ServiceItem("S3", "Scalable Storage in the Cloud", Icons.Default.Storage, CloudScreen.SERVICES_LIST, Color(0xFF0089D6), "s3"),
            ServiceItem("SageMaker AI", "Build, Train, and Deploy Machine Learning Models", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "sagemaker"),
            ServiceItem("Secrets Manager", "Easily rotate, manage, and retrieve secrets throughout their lifecycle", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "secrets"),
            ServiceItem("Security Hub CSPM", "Automated security checks across your AWS environment.", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "security_hub"),
            ServiceItem("AWS Security Incident Response", "Quickly prepare for, respond to, and recover from security incidents", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "security_incident"),
            ServiceItem("Service Quotas", "View and manage your AWS service quotas from a central location", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "service_quotas"),
            ServiceItem("Amazon Simple Email Service", "Email Sending and Receiving Service", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "ses"),
            ServiceItem("Simple Notification Service", "SNS managed message topics for Pub/Sub", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "sns"),
            ServiceItem("Simple Queue Service", "Message Queue Service", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "sqs"),
            ServiceItem("Step Functions", "Coordinate Distributed Applications", Icons.Default.Hub, CloudScreen.SERVICES_LIST, Color(0xFF00E5FF), "step_functions"),
            ServiceItem("Support", "Contact AWS for technical and account support.", Icons.Default.Info, CloudScreen.SERVICES_LIST, Color(0xFF49454F), "support"),
            ServiceItem("Systems Manager", "AWS Systems Manager is a Central Place to View and Manage AWS Resources", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "systems_manager"),
            ServiceItem("Amazon Textract", "Easily extract text and data from virtually any document", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "textract"),
            ServiceItem("Amazon Transcribe", "Powerful Speech Recognition", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "transcribe"),
            ServiceItem("AWS Transform", "AI agents to accelerate and simplify migration and modernization", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "transform"),
            ServiceItem("Amazon Translate", "Powerful Neural Machine Translation", Icons.Default.SmartToy, CloudScreen.SERVICES_LIST, Color(0xFF7C4DFF), "translate"),
            ServiceItem("Trusted Advisor", "Optimize performance, improve security, reduce costs", Icons.Default.Analytics, CloudScreen.SERVICES_LIST, Color(0xFF2979FF), "trusted_advisor"),
            ServiceItem("VPC", "Isolated Cloud Resources", Icons.Default.Router, CloudScreen.SERVICES_LIST, Color(0xFF1B5E20), "vpc"),
            ServiceItem("WAF & Shield", "Protects Against DDoS Attacks and Malicious Web Traffic", Icons.Default.Security, CloudScreen.SERVICES_LIST, Color(0xFFB3261E), "waf_shield"),
            ServiceItem("Amazon WorkMail", "Secure Email and Calendaring Service", Icons.Default.Info, CloudScreen.SERVICES_LIST, Color(0xFF49454F), "workmail"),
            ServiceItem("WorkSpaces", "Desktops in the Cloud", Icons.Default.Info, CloudScreen.SERVICES_LIST, Color(0xFF49454F), "workspaces")
        )
    }

    // Combine standard services and Core SRE services
    val allServices = remember { coreSreServices + standardAwsServices }

    // Filter services based on query and category
    val filteredServices = remember(searchQuery, selectedCategory) {
        allServices.filter {
            val matchesSearch = it.title.contains(searchQuery, ignoreCase = true) ||
                    it.description.contains(searchQuery, ignoreCase = true)
            val matchesCategory = when (selectedCategory) {
                "All" -> true
                "SRE Hub" -> it.isCoreSre
                "AWS Services" -> !it.isCoreSre
                "Compute" -> it.accentColor == Color(0xFFFF9900)
                "Database" -> it.accentColor == Color(0xFF0089D6)
                "Security" -> it.accentColor == Color(0xFFB3261E)
                else -> true
            }
            matchesSearch && matchesCategory
        }
    }

    // SRE Telemetry Log Generator helper
    fun generateDiagnosticLogs(serviceTitle: String, region: String): List<String> {
        val sdf = SimpleDateFormat("HH:mm:ss.SSS", Locale.US)
        val timestamp = sdf.format(Date())
        return when (serviceTitle) {
            "EC2" -> listOf(
                "[$timestamp INFO] Establishing regional SRE connection to ap-south-1...",
                "[$timestamp SECURE] Auditing security configurations and host virtualization...",
                "[$timestamp WARNING] Port 22 (SSH) is open to 0.0.0.0/0 on 2 active Web tiers (web-node-01, web-node-02).",
                "[$timestamp SPEED] Latency: 2.4ms. Host hypervisor diagnostics: STABLE.",
                "[$timestamp SUCCESS] EC2 Scan Complete. Suggested actions: Apply Terraform patches in 'HCL Migrate'."
            )
            "S3" -> listOf(
                "[$timestamp INFO] Connecting to AWS S3 Object Storage API...",
                "[$timestamp CHECK] Scanning active buckets in regional cluster $region...",
                "[$timestamp WARNING] Bucket 's3-corporate-archive-992' contains 14.2TB of raw unencrypted archive logs.",
                "[$timestamp SECURE] Verifying public access block settings: ALL ENABLED.",
                "[$timestamp SUCCESS] S3 Scan complete. Zero data leak anomalies identified. Suggested action: Enable default KMS encryption tags."
            )
            "DynamoDB" -> listOf(
                "[$timestamp INFO] Polling DynamoDB metadata schema and partition index allocations...",
                "[$timestamp METRICS] WCU: 140/800. RCU: 450/1000. Partition splits: 0.",
                "[$timestamp SECURE] Point-in-time recovery (PITR) status: ENABLED.",
                "[$timestamp SPEED] Global Tables sync latency to us-east-1: 12ms (OPTIMAL).",
                "[$timestamp SUCCESS] DynamoDB database clusters are thoroughly HEALTHY."
            )
            "WAF & Shield" -> listOf(
                "[$timestamp SRE] Querying AWS WAF Access Control Lists active rules...",
                "[$timestamp SRE] Received: DDoS mitigation threshold is active at 10,000 req/min.",
                "[$timestamp INFO] Inspected 54,230 inbound packets from last 5 minutes.",
                "[$timestamp SECURE] Threat intelligence shield has BLACKLISTED 14 suspected bot IPs.",
                "[$timestamp SUCCESS] WAF state: SECURE. Shield Advanced coverage confirmed."
            )
            "SRE Plane" -> listOf(
                "[$timestamp SYSTEM] Initializing autonomous SRE map coordinator...",
                "[$timestamp SYSTEM] Parsing 24 nodes and 36 network edges in Neo4j dependency vault...",
                "[$timestamp INFO] Link quality: Primary cluster nodes fully interconnected.",
                "[$timestamp SUCCESS] SRE plane telemetry successfully linked and mapped. Visual graph active."
            )
            "Autonomous Diagnosis" -> listOf(
                "[$timestamp AI-DOCTOR] Scanning active system alerts and CloudWatch event buffers...",
                "[$timestamp WARNING] High CPU usage trigger caught on DB-Replica-01 instance.",
                "[$timestamp AI-DOCTOR] Programmatically launching scale-out script via FastAPI daemon...",
                "[$timestamp SUCCESS] Root cause mitigated. System recovery loop returned status: RESOLVED."
            )
            else -> listOf(
                "[$timestamp INFO] Establishing connection probe to $serviceTitle...",
                "[$timestamp SRE] Testing authorization permissions and CORS options...",
                "[$timestamp METRICS] Health status index: 1.0 (HEALTHY). Active socket endpoints: 1.",
                "[$timestamp SUCCESS] Diagnostics completed for $serviceTitle. No critical failures detected."
            )
        }
    }

    // Trigger sequential diagnostics simulation
    fun startDiagnostics(service: ServiceItem) {
        activeDiagnosticsJob?.cancel()
        logTerminalLines = emptyList()
        isScanning = true
        activeDiagnosticsJob = scope.launch {
            selectedServiceForDiagnostics = service
            if (service.tag == "aws_logs") {
                viewModel.fetchAwsLogs()
                delay(400)
                isScanning = false
                return@launch
            }
            val rawLogs = generateDiagnosticLogs(service.title, selectedRegion)
            logTerminalLines = logTerminalLines + "📡 [SOCKET] Dialing diagnostic probe for ${service.title} in region $selectedRegion..."
            delay(250)
            rawLogs.forEach { line ->
                delay(300)
                logTerminalLines = logTerminalLines + line
            }
            isScanning = false
        }
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(if (isDarkTheme) Color(0xFF0F0E13) else BentoBg)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(bottom = if (selectedServiceForDiagnostics != null) 240.dp else 0.dp) // Leave space for terminal drawer
        ) {
            // Top App Bar/Headers matching AWS console
            Card(
                modifier = Modifier
                    .fillMaxWidth(),
                shape = RoundedCornerShape(0.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (isDarkTheme) Color(0xFF151419) else Color(0xFFF6F3FB)
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "AWS CONSOLE EXPLORER",
                                color = BentoTextSubtitle,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "Services",
                                fontSize = 24.sp,
                                fontWeight = FontWeight.ExtraBold,
                                color = if (isDarkTheme) Color.White else BentoTextDark,
                                modifier = Modifier.testTag("services_title")
                            )
                        }

                        // Region indicator
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(if (isDarkTheme) Color(0xFF25232E) else BentoContainerActive)
                                .padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    imageVector = Icons.Default.LocationOn,
                                    contentDescription = "Region",
                                    tint = if (isDarkTheme) CyberCyan else BentoPurplePrimary,
                                    modifier = Modifier.size(14.dp)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = when (selectedRegion) {
                                        "ap-south-1" -> "Mumbai"
                                        "us-east-1" -> "N. Virginia"
                                        "ap-southeast-1" -> "Singapore"
                                        else -> "Region: $selectedRegion"
                                    },
                                    color = if (isDarkTheme) Color.White else BentoTextDark,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    // Real AWS-style search capsule
                    TextField(
                        value = searchQuery,
                        onValueChange = { searchQuery = it },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(52.dp)
                            .testTag("aws_services_search_bar"),
                        placeholder = {
                            Text(
                                "Search services or resources...",
                                fontSize = 14.sp,
                                color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle
                            )
                        },
                        leadingIcon = {
                            Icon(
                                imageVector = Icons.Default.Search,
                                contentDescription = "Search",
                                tint = if (isDarkTheme) Color.White else BentoTextSubtitle
                            )
                        },
                        trailingIcon = {
                            Icon(
                                imageVector = Icons.Default.Mic,
                                contentDescription = "Voice Search",
                                tint = if (isDarkTheme) Color.White else BentoTextSubtitle
                            )
                        },
                        shape = RoundedCornerShape(26.dp),
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = if (isDarkTheme) Color(0xFF22202C) else Color.White,
                            unfocusedContainerColor = if (isDarkTheme) Color(0xFF1E1C24) else Color(0xFFFFFAFA),
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent,
                            focusedTextColor = if (isDarkTheme) Color.White else BentoTextDark,
                            unfocusedTextColor = if (isDarkTheme) Color.White else BentoTextDark
                        ),
                        singleLine = true
                    )
                }
            }

            // Quick Filters (All, SRE Hub, AWS Services, Compute, Database, Security)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp, vertical = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                val categories = listOf("All", "SRE Hub", "AWS Services", "Compute", "Database", "Security")
                categories.forEach { category ->
                    val isSelected = selectedCategory == category
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(16.dp))
                            .background(
                                if (isSelected) {
                                    if (isDarkTheme) CyberCyan else BentoPurplePrimary
                                } else {
                                    if (isDarkTheme) Color(0xFF1E1C24) else Color(0xFFE8DEF8).copy(alpha = 0.5f)
                                }
                            )
                            .clickable { selectedCategory = category }
                            .padding(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = category,
                            color = if (isSelected) {
                                if (isDarkTheme) Color.Black else Color.White
                            } else {
                                if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle
                            },
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            // Services list container
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(filteredServices) { service ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                if (service.tag == "billing" || service.tag == "cost_explorer") {
                                    onNavigateToScreen(CloudScreen.COST_EXPLORER)
                                } else if (service.tag == "ec2") {
                                    onNavigateToScreen(CloudScreen.DASHBOARD)
                                    // Let Dashboard figure out it's EC2 via state if needed, but wait:
                                    // if it's ec2 we may want to show the instances. But in MainActivity we used onNavigateToScreen anyway, so we just use the enum.
                                    startDiagnostics(service) // we still run diagnostics to show logs if they want.
                                } else if (service.isCoreSre) {
                                    startDiagnostics(service)
                                } else {
                                    startDiagnostics(service)
                                }
                            }
                            .testTag("service_item_${service.tag}"),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = if (isDarkTheme) Color(0xFF1E1C24) else Color.White
                        ),
                        border = if (selectedServiceForDiagnostics?.title == service.title) {
                            BorderStroke(1.dp, if (isDarkTheme) CyberCyan else BentoPurplePrimary)
                        } else null,
                        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // Service Icon Left Container
                            Box(
                                modifier = Modifier
                                    .size(44.dp)
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(service.accentColor.copy(alpha = 0.15f)),
                                contentAlignment = Alignment.Center
                            ) {
                                val searchKeys = listOf(
                                    service.title.replace(" ", "").lowercase(),
                                    "amazon" + service.title.replace(" ", "").lowercase(),
                                    "aws" + service.title.replace(" ", "").lowercase(),
                                    service.tag.replace("_", "").lowercase(),
                                    "amazon" + service.tag.replace("_", "").lowercase(),
                                    "aws" + service.tag.replace("_", "").lowercase()
                                )
                                val matchedAsset = searchKeys.firstNotNullOfOrNull { assetMap[it] } ?: assetMap.values.find { it.contains(service.tag.replace("_",""), ignoreCase = true) }
                                
                                if (matchedAsset != null && !service.isCoreSre) {
                                    AsyncImage(
                                        model = ImageRequest.Builder(LocalContext.current)
                                            .data("file:///android_asset/$matchedAsset")
                                            .crossfade(true)
                                            .build(),
                                        contentDescription = service.title,
                                        modifier = Modifier.size(28.dp).clip(RoundedCornerShape(4.dp))
                                    )
                                } else {
                                    Icon(
                                        imageVector = service.icon,
                                        contentDescription = service.title,
                                        tint = service.accentColor,
                                        modifier = Modifier.size(24.dp)
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.width(12.dp))

                            // Title & Description
                            Column(
                                modifier = Modifier.weight(1f)
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(
                                        text = service.title,
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isDarkTheme) Color.White else BentoTextDark
                                    )
                                    if (service.isCoreSre) {
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Box(
                                            modifier = Modifier
                                                .clip(RoundedCornerShape(4.dp))
                                                .background(BentoPurplePrimary.copy(alpha = 0.2f))
                                                .padding(horizontal = 4.dp, vertical = 2.dp)
                                        ) {
                                            Text(
                                                "SRE TOOL",
                                                color = if (isDarkTheme) CyberCyan else BentoPurpleDark,
                                                fontSize = 9.sp,
                                                fontWeight = FontWeight.Bold
                                            )
                                        }
                                    }
                                }
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = service.description,
                                    fontSize = 12.sp,
                                    color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle,
                                    lineHeight = 16.sp
                                )
                            }

                            // Interactive Right Control Button
                            IconButton(
                                onClick = {
                                    if (service.isCoreSre) {
                                        onNavigateToScreen(service.screen)
                                    } else {
                                        startDiagnostics(service)
                                    }
                                }
                            ) {
                                Icon(
                                    imageVector = if (service.isCoreSre) Icons.Default.Launch else Icons.Default.BarChart,
                                    contentDescription = "Diagnostics",
                                    tint = if (selectedServiceForDiagnostics?.title == service.title) {
                                        if (isDarkTheme) CyberCyan else BentoPurplePrimary
                                    } else {
                                        if (isDarkTheme) Color(0xFF81C784) else BentoTextSubtitle
                                    },
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                        }
                    }
                }

                if (filteredServices.isEmpty()) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(32.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = "No matching services found in current region.",
                                color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle,
                                fontSize = 14.sp
                            )
                        }
                    }
                }
            }
        }

        // --- GORGEOUS SRE TELEMETRY LOG TELEVISION DRAWER ---
        AnimatedVisibility(
            visible = selectedServiceForDiagnostics != null,
            modifier = Modifier.align(Alignment.BottomCenter),
            enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
            exit = slideOutVertically(targetOffsetY = { it }) + fadeOut()
        ) {
            val service = selectedServiceForDiagnostics
            if (service != null) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(240.dp)
                        .testTag("sre_live_terminal"),
                    shape = RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFF151419) // Always dark/slate terminal
                    ),
                    elevation = CardDefaults.cardElevation(defaultElevation = 16.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(12.dp)
                    ) {
                        // Terminal Header Bar
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                // Pulsing healthy/active indicator
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .clip(CircleShape)
                                        .background(if (isScanning) Color.Green else Color(0xFF00FF66))
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "SRE DIAGNOSTICS: ${service.title.uppercase()} @ $selectedRegion",
                                    fontFamily = FontFamily.Monospace,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 11.sp,
                                    color = Color.White
                                )
                            }

                            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                if (service.isCoreSre) {
                                    Button(
                                        onClick = { onNavigateToScreen(service.screen) },
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = BentoPurplePrimary,
                                            contentColor = Color.White
                                        ),
                                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 2.dp),
                                        shape = RoundedCornerShape(6.dp),
                                        modifier = Modifier.height(24.dp)
                                    ) {
                                        Text("Launch Hub", fontSize = 10.sp, fontWeight = FontWeight.Bold)
                                    }
                                }

                                IconButton(
                                    onClick = { startDiagnostics(service) },
                                    modifier = Modifier.size(24.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Refresh,
                                        contentDescription = "Rerun Diagnostics",
                                        tint = Color.White,
                                        modifier = Modifier.size(16.dp)
                                    )
                                }

                                IconButton(
                                    onClick = {
                                        activeDiagnosticsJob?.cancel()
                                        selectedServiceForDiagnostics = null
                                        logTerminalLines = emptyList()
                                    },
                                    modifier = Modifier.size(24.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Close,
                                        contentDescription = "Collapse Terminal",
                                        tint = Color.White,
                                        modifier = Modifier.size(16.dp)
                                    )
                                }
                            }
                        }

                        Divider(
                            modifier = Modifier.padding(vertical = 8.dp),
                            color = Color(0xFF2C2A35)
                        )

                        val scrollState = rememberScrollState()
                        val activeLogList = if (selectedServiceForDiagnostics?.tag == "aws_logs") awsLogs else logTerminalLines

                        LaunchedEffect(activeLogList.size) {
                            scrollState.animateScrollTo(scrollState.maxValue)
                        }

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .weight(1f)
                                .verticalScroll(scrollState)
                        ) {
                            if (activeLogList.isEmpty() && isScanning) {
                                Text(
                                    text = "Connecting to telemetry socket...",
                                    color = Color.Gray,
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 11.sp
                                )
                            }

                            activeLogList.forEach { line ->
                                if (selectedServiceForDiagnostics?.tag == "aws_logs") {
                                    AwsParsedLogItem(line)
                                } else {
                                    val color = when {
                                        line.contains("WARNING") -> WarningAmber
                                        line.contains("SECURE") -> CyberCyan
                                        line.contains("SUCCESS") -> TerminalGreen
                                        line.contains("HEALTHY") -> TerminalGreen
                                        line.contains("SRE") -> NebulaPurple
                                        line.contains("AI-DOCTOR") -> BentoAccentRed
                                        else -> Color.LightGray
                                    }
                                    Text(
                                        text = line,
                                        color = color,
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 11.sp,
                                        lineHeight = 15.sp
                                    )
                                    Spacer(modifier = Modifier.height(3.dp))
                                }
                            }

                        }
                    }
                }
            }
        }
    }
}

@Composable
fun AwsParsedLogItem(line: String) {
    val regex = """\[(.*?)\] \[AWS\] \[REGION: (.*?)\] \[SERVICE: (.*?)\] \[ACTION: (.*?)\] \[STATUS: (.*?)\] - (.*)""".toRegex()
    val match = regex.find(line)

    if (match != null) {
        val (timestamp, region, service, action, status, details) = match.destructured

        val statusColor = when (status) {
            "SUCCESS" -> Color(0xFF00C853)
            "ERROR", "FAILED" -> Color(0xFFE53935)
            else -> Color.Gray
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1C26)),
            shape = RoundedCornerShape(8.dp),
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp)
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Terminal,
                            contentDescription = null,
                            tint = Color(0xFFFF9900),
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "AWS ${service.uppercase()}",
                            color = Color.White,
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 13.sp
                        )
                    }
                    Text(
                        text = timestamp.split(" ").lastOrNull() ?: timestamp,
                        color = Color.Gray,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace
                    )
                }
                Spacer(modifier = Modifier.height(10.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    AwsLogChip(label = action, valueColor = CyberCyan)
                    AwsLogChip(label = region, valueColor = NebulaPurple)
                    AwsLogChip(label = status, valueColor = statusColor)
                }

                if (details.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = details,
                        color = Color.LightGray,
                        fontSize = 12.sp,
                        lineHeight = 16.sp
                    )
                }
            }
        }
    } else {
        // Fallback for unparsed logs or plain terminal text
        Text(
            text = line,
            color = Color.LightGray,
            fontFamily = FontFamily.Monospace,
            fontSize = 11.sp,
            lineHeight = 15.sp
        )
        Spacer(modifier = Modifier.height(3.dp))
    }
}

@Composable
fun AwsLogChip(label: String, valueColor: Color) {
    Surface(
        color = Color(0xFF2C2A35),
        shape = RoundedCornerShape(4.dp)
    ) {
        Text(
            text = label,
            color = valueColor,
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold,
            fontFamily = FontFamily.Monospace,
            modifier = Modifier.padding(horizontal = 6.dp, vertical = 3.dp)
        )
    }
}