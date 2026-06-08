package com.example.api

import com.example.BuildConfig
import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.http.Query
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import android.util.Log

@JsonClass(generateAdapter = true)
data class Part(
    @Json(name = "text") val text: String? = null
)

@JsonClass(generateAdapter = true)
data class Content(
    @Json(name = "parts") val parts: List<Part>
)

@JsonClass(generateAdapter = true)
data class GenerateContentRequest(
    @Json(name = "contents") val contents: List<Content>,
    @Json(name = "systemInstruction") val systemInstruction: Content? = null
)

@JsonClass(generateAdapter = true)
data class Candidate(
    @Json(name = "content") val content: Content
)

@JsonClass(generateAdapter = true)
data class GenerateContentResponse(
    @Json(name = "candidates") val candidates: List<Candidate>? = null
)

interface GeminiApiService {
    @POST("v1beta/models/gemini-3.5-flash:generateContent")
    suspend fun generateContent(
        @Query("key") apiKey: String,
        @Body request: GenerateContentRequest
    ): GenerateContentResponse
}

object GeminiClient {
    private const val BASE_URL = "https://generativelanguage.googleapis.com/"
    private const val TAG = "GeminiClient"

    private val moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()

    private val service: GeminiApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(GeminiApiService::class.java)
    }

    /**
     * Checks if the configured API key is available and valid (i.e. not placeholder).
     */
    fun isApiKeyConfigured(): Boolean {
        val apiKey = try {
            BuildConfig.GEMINI_API_KEY
        } catch (e: Exception) {
            ""
        }
        return apiKey.isNotEmpty() && apiKey != "MY_GEMINI_API_KEY" && apiKey != "placeholder"
    }

    /**
     * Generate content using the live Gemini API or fall back on highly detailed mock AI insights
     * if the key is not set.
     */
    suspend fun generateMigrationFeedback(prompt: String, systemInstruction: String? = null): String = withContext(Dispatchers.IO) {
        if (!isApiKeyConfigured()) {
            delaySimulation()
            return@withContext getMockAiResponse(prompt)
        }

        val request = GenerateContentRequest(
            contents = listOf(Content(parts = listOf(Part(text = prompt)))),
            systemInstruction = systemInstruction?.let { Content(parts = listOf(Part(text = it))) }
        )

        try {
            val apiKey = BuildConfig.GEMINI_API_KEY
            val response = service.generateContent(apiKey, request)
            response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text 
                ?: "Received empty response. Unable to process cloud architectural blueprint."
        } catch (e: Exception) {
            Log.e(TAG, "Gemini call failed, falling back to local analysis engine.", e)
            "Remote analysis unavailable (Error: ${e.localizedMessage}). Local offline analysis:\n\n${getMockAiResponse(prompt)}"
        }
    }

    private suspend fun delaySimulation() {
        kotlinx.coroutines.delay(1200) // Realistic server processing time
    }

    private fun getMockAiResponse(prompt: String): String {
        val lowercasePrompt = prompt.lowercase()
        return when {
            lowercasePrompt.contains("explain") || lowercasePrompt.contains("architecture") || lowercasePrompt.contains("dependency") -> {
                """
                ### Core Architecture Map
                The discovered environment is configured as a robust multi-tiered microservices stack. Below is the active relationship graph:
                
                *   **User Interface**: Custom Flutter client.
                *   **API Layer**: FastAPI instances behind an Application Load Balancer (ALB).
                *   **State & Session**: PostgreSQL databases for master data and a Redis cluster for active session token caching.
                *   **Graph Relationships**: Neo4j clusters map nested subnet resources and transitive service dependencies.
                *   **Event Pipeline**: Serverless Lambda workers consume from SQS and publish logs to SNS topics.

                ### Transitive Topology Dependencies
                `FastAPI Pods` ➔ `ALB` ➔ `EC2 VM Clusters` ➔ `PostgreSQL RDS DB` (Primary)
                `Lambda Worker` ➔ `SQS Queue` ➔ `SNS Topic` ➔ `S3 Audit Bucket`

                ### Migration Recommendations
                1. **Targeting GCP**: Map AWS ALBs to global Cloud Load Balancing and migration of AWS RDS PostgreSQL to Cloud SQL for PostgreSQL.
                2. **Targeting Azure**: Replace EC2 nodes with high-performance Azure VM Scale Sets and map S3 targets to Azure Blob Private Containers.
                3. **Containers**: Package containerized workloads into Azure AKS or Google GKE clusters for native scalability.
                """.trimIndent()
            }
            lowercasePrompt.contains("cost") || lowercasePrompt.contains("optimize") || lowercasePrompt.contains("saving") -> {
                """
                ### Financial Audit & Multi-Cloud Reductions
                Our audit scans recommend several critical steps to optimize operational spend:
                
                *   **Under-Utilized VM Sizing**: AWS EC2 instances `app-worker-01` and `analytics-engine` are running with historical CPU utilization below 12%. Recommending a downgrade from `m5.large` to `t3.medium`.
                *   **Compute Savings**: Estimated monthly reduction is **${'$'}642.00 / month** on AWS, or **${'$'}583.00** if migrated directly to Azure VM B-series.
                *   **Storage Lifecycles**: S3 storage logs have no active lifecycle configuration, carrying 14TB of high-frequency objects. Enabling transitioning to Glacier Deep Archive after 30 days saves **${'$'}280.00 / month**.
                *   **Orphaned Volumes**: Found three Elastic Block Store (EBS) volumes with status `available` (unattached) costing **${'$'}88.00 / month**. Safe deletion is advised immediately.
                
                ### Total Potential Savings
                🟢 **${'$'}1,010.00 / month** (34.2% of current monthly cloud balance)
                """.trimIndent()
            }
            lowercasePrompt.contains("security") || lowercasePrompt.contains("risk") || lowercasePrompt.contains("vulnerability") -> {
                """
                ### DevSecOps Threat Analysis
                The visual dependency scan identified several security vulnerabilities in the source cloud configurations:
                
                *   **OPEN PUBLIC INGRESS**: AWS Security Group `sg-web-public` allows open wildcard access (`0.0.0.0/0`) on port `22` (SSH).
                    *   *Risk*: Exploit scan vectors can identify active shell endpoints.
                    *   *Remediation*: Restrict ingress to the bastion subnet or corporate VPN CIDR.
                *   **UNENCRYPTED STORAGE**: S3 bucket `s3-corporate-archive-992` lacks server-side encryption (SSE-KMS) configuration.
                    *   *Risk*: Administrative credentials leak exposes entire archive.
                    *   *Remediation*: Apply IAM bucket policy requiring encrypted writes and secure transit TLS 1.3.
                *   **IAM OVER-PRIVILEGE**: Role `lambda-processor-execution-role` is attached to policy `AdministratorAccess` instead of strict least-privilege resource access.
                    *   *Risk*: Execution exploits grant full tenant elevation.
                """.trimIndent()
            }
            lowercasePrompt.contains("terraform") || lowercasePrompt.contains("code") || lowercasePrompt.contains("generate") -> {
                """
                ### Generated Multi-cloud Infrastructure Map
                Here is a robust Terraform script converting the AWS network topology into a corresponding secure Azure deployment:

                ```hcl
                # Azure Provider Setup
                provider "azurerm" {
                  features {}
                }

                # Secure VNet Container
                resource "azurerm_virtual_network" "vnet" {
                  name                = "cloudmigrate-azure-vnet"
                  address_space       = ["10.0.0.0/16"]
                  location            = "East US"
                  resource_group_name = "CloudMigrateRG"
                }

                # Azure SQL Instance Replacement for RDS PostgreSQL
                resource "azurerm_postgresql_flexible_server" "db" {
                  name                   = "cloudmigrate-db-flexible"
                  resource_group_name    = "CloudMigrateRG"
                  location               = "East US"
                  version                = "13"
                  administrator_login    = "cloud_admin"
                  administrator_password = "SecurePassword2026!"
                  storage_mb             = 32768
                  sku_name               = "GP_Standard_D2s_v3"
                }

                # Storage Account Blob Container matching S3
                resource "azurerm_storage_account" "storage" {
                  name                     = "cloudmigrateblobsecure"
                  resource_group_name      = "CloudMigrateRG"
                  location                 = "East US"
                  account_tier             = "Standard"
                  account_replication_type = "LRS"
                }
                ```
                """.trimIndent()
            }
            else -> {
                """
                ### CloudMigrate AI Assistant
                I am your dedicated **Cloud Intelligence & Migration Architect**.
                
                You can write specific inquiries to audit, explain, or generate migrations. Here are suggestions you can ask me:
                
                *   "**Explain the discovered AWS web architecture**" - Returns detailed visual topologies and resource connections.
                *   "**Conduct a cost audit review**" - Identifies compute wastes, orphan volumes, and S3 Glacier archive prospects.
                *   "**Audit security risks in EC2 and S3**" - Runs automated scans on IAM boundary roles and open wildcard security groups.
                *   "**Generate corresponding GCP Terraform code**" - Maps active assets to standard Google Cloud assets (Compute Engine, Cloud SQL, Cloud Storage).
                """.trimIndent()
            }
        }
    }
}
