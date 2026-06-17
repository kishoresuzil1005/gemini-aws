package com.example.api

import com.example.BuildConfig
import com.example.data.CloudAccount
import com.example.data.DiscoveryResource
import com.example.data.SavedMigration
import com.example.ui.BackgroundJob
import com.example.ui.CloudIncident
import com.squareup.moshi.JsonClass
import com.squareup.moshi.Json
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.*
import java.util.concurrent.TimeUnit
import android.util.Log

@JsonClass(generateAdapter = true)
data class AwsRegion(
    val name: String,
    val endpoint: String
)

@JsonClass(generateAdapter = true)
data class RegionsResponse(
    val success: Boolean,
    val regions: List<AwsRegion>
)

@JsonClass(generateAdapter = true)
data class AwsConnectRequest(
    val account_name: String,
    val account_id: String,
    val role_arn: String,
    val external_id: String? = null
)

@JsonClass(generateAdapter = true)
data class AwsConnectResponse(
    val success: Boolean,
    val account_id: Int
)

@JsonClass(generateAdapter = true)
data class SelfHealResponse(
    val status: String,
    val message: String,
    val incidentStatus: String,
    val logs: List<String>
)

@JsonClass(generateAdapter = true)
data class UserRegisterRequest(
    val email: String,
    val password: String,
    val organizationName: String,
    val plan: String = "BASIC",
    val role: String = "ORG_ADMIN"
)

@JsonClass(generateAdapter = true)
data class UserLoginRequest(
    val email: String,
    val password: String
)

@JsonClass(generateAdapter = true)
data class AuthTokenResponse(
    val accessToken: String,
    val tokenType: String,
    val userId: Int,
    val userEmail: String,
    val organizationName: String,
    val organizationId: Int,
    val plan: String,
    val role: String? = "ORG_ADMIN"
)

@JsonClass(generateAdapter = true)
data class AwsConnectPayload(
    val roleArn: String,
    val region: String,
    val accountName: String
)

@JsonClass(generateAdapter = true)
data class AzureConnectPayload(
    val tenantId: String,
    val clientId: String,
    val clientSecret: String,
    val region: String,
    val accountName: String
)

@JsonClass(generateAdapter = true)
data class GcpConnectPayload(
    val serviceAccountJson: String,
    val region: String,
    val accountName: String
)

@JsonClass(generateAdapter = true)
data class CloudAccountInner(
    val id: Int,
    val provider: String,
    val name: String,
    val accountId: String?,
    val roleArn: String?,
    val region: String,
    val status: String
)

@JsonClass(generateAdapter = true)
data class CloudConnectResponse(
    val status: String,
    val message: String,
    val account: CloudAccountInner
)

@JsonClass(generateAdapter = true)
data class TemporaryCredentialsResponse(
    val accountId: String?,
    val provider: String,
    val region: String,
    val status: String,
    val assumedRole: String?,
    val credentialsType: String,
    val credentials: Map<String, String>,
    val permissions: List<String>
)

@JsonClass(generateAdapter = true)
data class DirectCostService(
    val service: String,
    val amount: Double
)

@JsonClass(generateAdapter = true)
data class DirectCostDaily(
    val date: String,
    val amount: Double
)

@JsonClass(generateAdapter = true)
data class CloudCostSummary(
    val month: String,
    val actualCost: Double,
    val forecastCost: Double,
    val currency: String,
    val byService: List<DirectCostService>,
    val dailyTrend: List<DirectCostDaily>
)

@JsonClass(generateAdapter = true)
data class ResourceSummary(
    val totalResources: Int,
    val countsByType: Map<String, Int>
)

@JsonClass(generateAdapter = true)
data class DashboardSummary(
    val region: String?,
    val total_resources: Int,
    val running_resources: Int,
    val stopped_resources: Int,
    val region_count: Int,
    val provider_count: Int,
    val ec2: Int,
    val s3: Int,
    val rds: Int,
    @Json(name = "lambda") val lambdaCount: Int,
    val vpc: Int,
    val iam: Int,
    val ebs: Int,
    val service_breakdown: Map<String, Int>
)

@JsonClass(generateAdapter = true)
data class GraphNode(
    val id: String,
    val type: String,
    val name: String
)

@JsonClass(generateAdapter = true)
data class GraphEdge(
    val source: String,
    val target: String,
    val type: String
)

@JsonClass(generateAdapter = true)
data class GraphResponse(
    val nodes: List<GraphNode>,
    val edges: List<GraphEdge>
)

@JsonClass(generateAdapter = true)
data class TopologyCategory(
    val name: String,
    val count: Int
)

@JsonClass(generateAdapter = true)
data class TopologyResource(
    val id: String,
    val type: String,
    val name: String,
    val region: String,
    val status: String
)

@JsonClass(generateAdapter = true)
data class TopologyLevel3Resource(
    val id: String,
    val name: String
)

@JsonClass(generateAdapter = true)
data class TopologyLevel3Dependency(
    val type: String,
    val name: String
)

@JsonClass(generateAdapter = true)
data class TopologyLevel3Response(
    val resource: TopologyLevel3Resource,
    val dependencies: List<TopologyLevel3Dependency>
)

@JsonClass(generateAdapter = true)
data class GraphResourceNode(
    val id: String,
    val type: String,
    val name: String
)

@JsonClass(generateAdapter = true)
data class GraphResourceEdge(
    val source: String,
    val target: String,
    val relation: String
)

@JsonClass(generateAdapter = true)
data class ImpactedResource(
    val id: String,
    val type: String,
    val name: String,
    val impact: String
)

@JsonClass(generateAdapter = true)
data class ResourceGraphResponse(
    val resource: GraphResourceNode,
    val nodes: List<GraphResourceNode>,
    val edges: List<GraphResourceEdge>,
    val impact_analysis: List<ImpactedResource>
)

@JsonClass(generateAdapter = true)
data class RecommendationItem(
    val resource_id: String,
    val resource_name: String,
    val resource_type: String,
    val issue: String,
    val action: String,
    val savings: Double,
    val severity: String,
    val remediation_type: String
)

@JsonClass(generateAdapter = true)
data class OptimizationSavings(
    val monthly_savings: Double,
    val annual_savings: Double
)

@JsonClass(generateAdapter = true)
data class AIInsightsResponse(
    val executive_summary: String,
    val risks: List<String>,
    val savings_opportunities: List<String>,
    val recommendations: List<String>,
    val finops_score: Int
)

@JsonClass(generateAdapter = true)
data class AIChatPayload(
    val message: String
)

@JsonClass(generateAdapter = true)
data class AIChatResponse(
    val success: Boolean,
    val response: String
)

@JsonClass(generateAdapter = true)
data class EC2SummaryResponse(
    val running_instances: Int,
    val total_instances: Int,
    val instance_types: Int,
    val security_groups: Int,
    val elastic_ips: Int,
    val volumes: Int,
    val snapshots: Int
)

@JsonClass(generateAdapter = true)
data class EC2ExtendedResponse(
    val launch_templates: Int,
    val spot_requests: Int,
    val reserved_instances: Int,
    val dedicated_hosts: Int,
    val amis: Int,
    val ami_catalog: Int,
    val savings_plans: Int
)

@JsonClass(generateAdapter = true)
data class EC2RefreshResponse(
    val success: Boolean,
    val message: String
)

object TokenStorage {
    var jwtToken: String? = null
    var selectedRegion: String? = "ap-south-1"
}

interface CloudOpsApiService {
    @POST("api/cloud/aws/connect")
    suspend fun connectAwsPost(@Body request: AwsConnectRequest): AwsConnectResponse

    @GET("api/cloud/accounts/{accountId}/regions")
    suspend fun getAccountRegions(@Path("accountId") accountId: Int): RegionsResponse

    @POST("api/v1/auth/register")
    suspend fun register(@Body request: UserRegisterRequest): AuthTokenResponse

    @POST("api/v1/auth/login")
    suspend fun login(@Body request: UserLoginRequest): AuthTokenResponse

    @POST("api/v1/auth/logout")
    suspend fun logout(): Map<String, String>

    @GET("api/v1/auth/me")
    suspend fun getMe(): AuthTokenResponse

    @POST("api/cloud/connect/aws")
    suspend fun connectAws(@Body payload: AwsConnectPayload): CloudConnectResponse

    @POST("api/cloud/connect/azure")
    suspend fun connectAzure(@Body payload: AzureConnectPayload): CloudConnectResponse

    @POST("api/cloud/connect/gcp")
    suspend fun connectGcp(@Body payload: GcpConnectPayload): CloudConnectResponse

    @GET("api/cloud/credentials/{id}")
    suspend fun getTemporaryCredentials(@Path("id") id: Int): TemporaryCredentialsResponse

    @GET("api/accounts")
    suspend fun getAccounts(): List<CloudAccount>

    @POST("api/accounts")
    suspend fun addAccount(@Body account: CloudAccount): CloudAccount

    @DELETE("api/accounts/{id}")
    suspend fun deleteAccount(@Path("id") id: Int): Map<String, String>

    @GET("api/resources")
    suspend fun getResources(
        @Query("region") region: String? = null
    ): List<DiscoveryResource>

    @GET("api/resources/summary")
    suspend fun getResourcesSummary(
        @Query("region") region: String? = null
    ): ResourceSummary

    @GET("api/dashboard/summary")
    suspend fun getDashboardSummary(
        @Query("region") region: String? = null
    ): DashboardSummary

    @GET("api/regions")
    suspend fun getRegions(): List<String>

    @GET("api/ec2/summary")
    suspend fun getEC2Summary(
        @Query("region") region: String
    ): EC2SummaryResponse

    @GET("api/ec2/extended")
    suspend fun getEC2Extended(
        @Query("region") region: String
    ): EC2ExtendedResponse

    @POST("api/ec2/refresh")
    suspend fun refreshEC2(
        @Query("region") region: String
    ): EC2RefreshResponse

    @GET("api/topology")
    suspend fun getTopologySummary(): List<TopologyCategory>

    @GET("api/topology/{category}")
    suspend fun getTopologyResources(@Path("category") category: String): List<TopologyResource>

    @GET("api/topology/resource/{id}")
    suspend fun getTopologyLevel3(@Path("id") id: String): TopologyLevel3Response

    @GET("api/graph/resource/{id}")
    suspend fun getResourceGraph(@Path("id") id: String): ResourceGraphResponse

    @GET("api/graph")
    suspend fun getGraph(): GraphResponse

    @GET("api/incidents")
    suspend fun getIncidents(): List<CloudIncident>

    @POST("api/incidents/self-heal/{id}")
    suspend fun executeSelfHeal(@Path("id") incidentId: String): SelfHealResponse

    @POST("api/incidents/reset")
    suspend fun resetIncidents(): Map<String, String>

    @POST("api/discover")
    suspend fun triggerDiscovery(@Query("provider") provider: String): BackgroundJob

    @GET("api/jobs")
    suspend fun getJobs(): List<BackgroundJob>

    @GET("api/jobs/{id}")
    suspend fun getJobDetails(@Path("id") id: String): BackgroundJob

    @GET("api/migrations")
    suspend fun getMigrations(): List<SavedMigration>

    @POST("api/migrations")
    suspend fun saveMigration(@Body migration: SavedMigration): SavedMigration

    @DELETE("api/migrations/{id}")
    suspend fun deleteMigration(@Path("id") id: Int): Map<String, String>

    @GET("api/cost/summary")
    suspend fun getCostSummary(): CloudCostSummary

    @POST("api/cost/refresh")
    suspend fun refreshCostSummary(): CloudCostSummary

    @GET("api/optimization/recommendations")
    suspend fun getOptimizationRecommendations(): List<RecommendationItem>

    @GET("api/optimization/savings")
    suspend fun getOptimizationSavings(): OptimizationSavings

    @GET("api/ai/insights")
    suspend fun getAIInsights(): AIInsightsResponse

    @POST("api/ai/chat")
    suspend fun getAICopilotResponse(@Body payload: AIChatPayload): AIChatResponse
}

object CloudOpsBackendClient {
    private const val TAG = "CloudOpsBackendClient"
    
    private var customBaseUrl: String? = try {
        val url = BuildConfig.BACKEND_URL.trim().removeSurrounding("\"").removeSurrounding("'")
        if (url.isNotEmpty() && url != "placeholder") url else null
    } catch (e: Exception) {
        null
    }

    fun setCustomBaseUrl(url: String) {
        customBaseUrl = url
    }

    val baseUrl: String
        get() {
            var url = customBaseUrl ?: ""

            if (url.isBlank()) {
                throw IllegalStateException(
                    "Backend URL not configured"
                )
            }

            if (!url.startsWith("http://") &&
                !url.startsWith("https://")) {
                url = "http://$url"
            }

            Log.i(
                "BACKEND_DEBUG",
                "Using backend URL = $url"
            )

            return if (url.endsWith("/")) url else "$url/"
        }

    private val moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(200, TimeUnit.SECONDS)
        .readTimeout(200, TimeUnit.SECONDS)
        .writeTimeout(200, TimeUnit.SECONDS)
        .addInterceptor { chain ->
            val original = chain.request()
            val token = TokenStorage.jwtToken
            val region = TokenStorage.selectedRegion
            var requestBuilder = original.newBuilder()
            if (!token.isNullOrEmpty()) {
                requestBuilder = requestBuilder.header("Authorization", "Bearer $token")
            }
            if (!region.isNullOrEmpty()) {
                requestBuilder = requestBuilder.header("X-Selected-Region", region)
            }
            chain.proceed(requestBuilder.build())
        }
        .addInterceptor(loggingInterceptor)
        .build()

    private var cachedService: CloudOpsApiService? = null
    private var lastUsedBaseUrl: String? = null

    val service: CloudOpsApiService
        get() {
            val currentUrl = baseUrl
            synchronized(this) {
                if (cachedService == null || lastUsedBaseUrl != currentUrl) {
                    Log.i(TAG, "Initializing Retrofit with Base URL: $currentUrl")
                    lastUsedBaseUrl = currentUrl
                    cachedService = Retrofit.Builder()
                        .baseUrl(currentUrl)
                        .client(okHttpClient)
                        .addConverterFactory(MoshiConverterFactory.create(moshi))
                        .build()
                        .create(CloudOpsApiService::class.java)
                }
                return cachedService!!
            }
        }

    /**
     * Diagnostic utility to verify if the server is reachable and active.
     */
    fun isBackendConfigured(): Boolean {
        return try {
            baseUrl.isNotBlank()
        } catch (e: Exception) {
            false
        }
    }
}
