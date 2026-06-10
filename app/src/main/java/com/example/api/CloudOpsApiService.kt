package com.example.api

import com.example.BuildConfig
import com.example.data.CloudAccount
import com.example.data.DiscoveryResource
import com.example.data.SavedMigration
import com.example.ui.BackgroundJob
import com.example.ui.CloudIncident
import com.squareup.moshi.JsonClass
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
    val question: String
)

@JsonClass(generateAdapter = true)
data class AIChatResponse(
    val answer: String
)

object TokenStorage {
    var jwtToken: String? = null
}

interface CloudOpsApiService {
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
    suspend fun getResources(): List<DiscoveryResource>

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
    
    private var customBaseUrl: String? = null

    fun setCustomBaseUrl(url: String) {
        customBaseUrl = url
    }

    // Fall back to clean default URL if empty or not configured
    val baseUrl: String
        get() {
            var url = customBaseUrl ?: try {
                BuildConfig.BACKEND_URL.trim().removeSurrounding("\"").removeSurrounding("'")
            } catch (e: Exception) {
                ""
            }
            if (url.isNullOrEmpty() || url == "placeholder") {
                url = "http://10.0.2.2:8000/"
            }
            // Map 0.0.0.0 wildcard address to 10.0.2.2 for Android emulator routing compatibility
            if (url.contains("0.0.0.0")) {
                url = url.replace("0.0.0.0", "10.0.2.2")
            }
            // Ensure proper http/https protocol prefix
            if (!url.startsWith("http://") && !url.startsWith("https://")) {
                url = "http://$url"
            }
            return if (url.endsWith("/")) url else "$url/"
        }

    private val moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .addInterceptor { chain ->
            val original = chain.request()
            val token = TokenStorage.jwtToken
            val request = if (!token.isNullOrEmpty()) {
                original.newBuilder()
                    .header("Authorization", "Bearer $token")
                    .build()
            } else {
                original
            }
            chain.proceed(request)
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
        return baseUrl.contains("10.0.2.2") || baseUrl.contains("localhost") || baseUrl.startsWith("http")
    }
}
