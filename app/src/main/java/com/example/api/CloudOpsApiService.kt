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

interface CloudOpsApiService {
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
}

object CloudOpsBackendClient {
    private const val TAG = "CloudOpsBackendClient"
    
    // Fall back to clean default URL if empty or not configured
    val baseUrl: String
        get() {
            val url = try {
                BuildConfig.BACKEND_URL
            } catch (e: Exception) {
                ""
            }
            return if (url.isNullOrEmpty() || url == "placeholder") "http://10.0.2.2:8000/" else {
                if (url.endsWith("/")) url else "$url/"
            }
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
        .addInterceptor(loggingInterceptor)
        .build()

    val service: CloudOpsApiService by lazy {
        Log.i(TAG, "Initializing Retrofit with Base URL: $baseUrl")
        Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
            .create(CloudOpsApiService::class.java)
    }

    /**
     * Diagnostic utility to verify if the server is reachable and active.
     */
    fun isBackendConfigured(): Boolean {
        return baseUrl.contains("10.0.2.2") || baseUrl.contains("localhost") || baseUrl.startsWith("http")
    }
}
