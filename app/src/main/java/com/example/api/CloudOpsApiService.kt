package com.example.api

import com.example.BuildConfig
import com.example.data.CloudAccount
import com.example.data.DiscoveryResource
import com.example.data.SavedMigration
import com.example.ui.BackgroundJob
import com.example.ui.CloudIncident
import com.example.api.models.DashboardSummary
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

@JsonClass(generateAdapter = true)
<<<<<<< HEAD
@JsonClass(generateAdapter = true)
=======
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
data class EC2Instance(
    @Json(name = "instance_id") val instanceId: String,
    @Json(name = "instance_type") val instanceType: String,
    @Json(name = "state") val state: String,
    @Json(name = "region") val region: String,
    @Json(name = "public_ip") val publicIp: String?,
    @Json(name = "private_ip") val privateIp: String?
)

@JsonClass(generateAdapter = true)
data class EC2ActionRequest(
    @Json(name = "instance_id") val instance_id: String
)

@JsonClass(generateAdapter = true)
data class EC2ActionResponse(
    @Json(name = "status") val status: String
)

<<<<<<< HEAD
@JsonClass(generateAdapter = true)
data class EC2InstanceType(
    val type: String,
    val vcpus: Int,
    val memory: Int,
    val storage: String,
    val networkPerformance: String,
    val priceLinux: Double,
    val priceWindows: Double,
    val cpu_manufacturer: String?
)

@JsonClass(generateAdapter = true)
data class InstanceTypeAdviceRequest(
    val workloadType: String,
    val useCase: String,
    val priority: String,
    val cpuManufacturer: String
)

@JsonClass(generateAdapter = true)
data class EC2LaunchTemplate(
    val name: String,
    val templateId: String,
    val defaultVersion: Int,
    val latestVersion: Int,
    val createdBy: String,
    val createTime: String
)

@JsonClass(generateAdapter = true)
data class EC2SpotRequest(
    val requestId: String,
    val type: String,
    val state: String,
    val status: String,
    val instanceId: String,
    val maxPrice: String,
    val createTime: String
)

@JsonClass(generateAdapter = true)
data class EC2SavingsPlan(
    val planId: String,
    val type: String,
    val commitment: Double,
    val term: Long,
    val state: String,
    val startDate: String
)

@JsonClass(generateAdapter = true)
data class EC2ReservedInstance(
    val reservedId: String,
    val instanceType: String,
    val platform: String,
    val term: Long,
    val state: String,
    val count: Int,
    val scope: String
)

@JsonClass(generateAdapter = true)
data class EC2DedicatedHost(
    val hostId: String,
    val type: String,
    val az: String,
    val state: String,
    val totalVcpus: Int,
    val freeVcpus: Int,
    val instancesCount: Int
)

@JsonClass(generateAdapter = true)
data class EC2Ami(
    val imageId: String,
    val name: String,
    val source: String,
    val owner: String,
    val visibility: String,
    val status: String
)

@JsonClass(generateAdapter = true)
data class EC2AmiCatalogItem(
    val name: String,
    val description: String,
    val architecture: String,
    val os: String
)

@JsonClass(generateAdapter = true)
data class EC2Volume(
    val volumeId: String,
    val name: String,
    val size: Int,
    val type: String,
    val iops: Int,
    val throughput: Int,
    val snapshotId: String,
    val state: String,
    val attachment: String
)

@JsonClass(generateAdapter = true)
data class EC2Snapshot(
    val snapshotId: String,
    val name: String,
    val volumeId: String,
    val size: Int,
    val state: String,
    val startTime: String,
    val progress: String
)

@JsonClass(generateAdapter = true)
data class EC2SecurityGroup(
    val groupId: String,
    val name: String,
    val description: String,
    val vpcId: String,
    val inboundCount: Int,
    val outboundCount: Int
)

@JsonClass(generateAdapter = true)
data class EC2ElasticIp(
    val allocationId: String,
    val ip: String,
    val instanceId: String,
    val privateIp: String,
    val associationId: String,
    val reverseDns: String
)

@JsonClass(generateAdapter = true)
data class EC2PlacementGroup(
    val groupName: String,
    val state: String,
    val strategy: String,
    val partitionCount: Int,
    val groupId: String
)

@JsonClass(generateAdapter = true)
data class EC2KeyPair(
    val keyPairId: String,
    val name: String,
    val type: String,
    val fingerprint: String,
    val createTime: String
)

@JsonClass(generateAdapter = true)
data class EC2NetworkInterface(
    val eniId: String,
    val subnetId: String,
    val vpcId: String,
    val privateIp: String,
    val publicIp: String,
    val mac: String,
    val status: String,
    val owner: String,
    val description: String
)

@JsonClass(generateAdapter = true)
data class EC2LoadBalancer(
    val name: String,
    val state: String,
    val type: String,
    val scheme: String,
    val ipAddressType: String,
    val vpcId: String,
    val azs: List<String>,
    val securityGroups: List<String>,
    val dnsName: String
)

@JsonClass(generateAdapter = true)
data class EC2TargetGroup(
    val name: String,
    val arn: String,
    val port: Int,
    val protocol: String,
    val targetType: String,
    val loadBalancer: String,
    val vpcId: String
)

@JsonClass(generateAdapter = true)
data class EC2TrustStore(
    val name: String,
    val status: String,
    val arn: String,
    val loadBalancersCount: Int,
    val caCertificatesCount: Int,
    val revokedCertificatesCount: Int,
    val ownerId: String,
    val tags: List<Map<String, String>>? = null
)

=======
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
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

    @GET("api/ec2/instances")
    suspend fun getEC2Instances(
        @Query("region") region: String
    ): List<EC2Instance>

    @POST("api/ec2/start")
    suspend fun startEC2(
        @Body request: EC2ActionRequest
    ): EC2ActionResponse

    @POST("api/ec2/stop")
    suspend fun stopEC2(
        @Body request: EC2ActionRequest
    ): EC2ActionResponse

    @POST("api/ec2/reboot")
    suspend fun rebootEC2(
        @Body request: EC2ActionRequest
    ): EC2ActionResponse

<<<<<<< HEAD
    @GET("api/ec2/instance_types")
    suspend fun getEC2InstanceTypes(@Query("region") region: String): List<EC2InstanceType>

    @POST("api/ec2/instance_types/advice")
    suspend fun getEC2InstanceTypeAdvice(@Body request: InstanceTypeAdviceRequest, @Query("region") region: String): List<EC2InstanceType>

    @GET("api/ec2/launch_templates")
    suspend fun getEC2LaunchTemplates(@Query("region") region: String): List<EC2LaunchTemplate>

    @GET("api/ec2/spot_requests")
    suspend fun getEC2SpotRequests(@Query("region") region: String): List<EC2SpotRequest>

    @GET("api/ec2/savings_plans")
    suspend fun getEC2SavingsPlans(@Query("region") region: String): List<EC2SavingsPlan>

    @GET("api/ec2/reserved_instances")
    suspend fun getEC2ReservedInstances(@Query("region") region: String): List<EC2ReservedInstance>

    @GET("api/ec2/dedicated_hosts")
    suspend fun getEC2DedicatedHosts(@Query("region") region: String): List<EC2DedicatedHost>

    @GET("api/ec2/amis")
    suspend fun getEC2Amis(@Query("region") region: String): List<EC2Ami>

    @GET("api/ec2/ami_catalog")
    suspend fun getEC2AmiCatalog(@Query("region") region: String): List<EC2AmiCatalogItem>

    @GET("api/ec2/volumes")
    suspend fun getEC2Volumes(@Query("region") region: String): List<EC2Volume>

    @GET("api/ec2/snapshots")
    suspend fun getEC2Snapshots(@Query("region") region: String): List<EC2Snapshot>

    @GET("api/ec2/security_groups")
    suspend fun getEC2SecurityGroups(@Query("region") region: String): List<EC2SecurityGroup>

    @GET("api/ec2/elastic_ips")
    suspend fun getEC2ElasticIps(@Query("region") region: String): List<EC2ElasticIp>

    @GET("api/ec2/placement_groups")
    suspend fun getEC2PlacementGroups(@Query("region") region: String): List<EC2PlacementGroup>

    @GET("api/ec2/key_pairs")
    suspend fun getEC2KeyPairs(@Query("region") region: String): List<EC2KeyPair>

    @GET("api/ec2/network_interfaces")
    suspend fun getEC2NetworkInterfaces(@Query("region") region: String): List<EC2NetworkInterface>

    @GET("api/ec2/load_balancers")
    suspend fun getEC2LoadBalancers(@Query("region") region: String): List<EC2LoadBalancer>

    @GET("api/ec2/target_groups")
    suspend fun getEC2TargetGroups(@Query("region") region: String): List<EC2TargetGroup>

    @GET("api/ec2/trust_stores")
    suspend fun getEC2TrustStores(@Query("region") region: String): List<EC2TrustStore>

=======
>>>>>>> 13ea076bcd3898214a01f2dbc5ededca3ec1b4dc
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

    @GET("api/aws/logs")
    suspend fun getAwsLogs(): List<String>
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
