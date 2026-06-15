package com.example.ui

import android.app.Application
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.api.GeminiClient
import com.example.api.CloudOpsBackendClient
import com.example.api.CloudOpsApiService
import com.example.data.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

// Message class for AI Client Chat
data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val text: String,
    val isUser: Boolean,
    val timestamp: String = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
)

// Active background celery-like job representation
data class BackgroundJob(
    val id: String,
    val name: String,
    val progress: Float, // 0.0f to 1.0f
    val status: String, // "QUEUED", "RUNNING", "COMPLETED", "FAILED"
    val timestamp: String = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
)

// Incident model representing discovered threats or operational warnings
data class CloudIncident(
    val id: String,
    val title: String,
    val severity: String, // "CRITICAL", "WARNING", "HEALTHY"
    val resourceId: String,
    val description: String,
    val status: String, // "ACTIVE", "HEALING", "RESOLVED"
    val timestamp: String = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
)

// Self-healing event audit log
data class SelfHealAction(
    val id: String,
    val incidentId: String,
    val actionName: String,
    val status: String, // "EXECUTING", "SUCCESS", "FAILED"
    val timestamp: String = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
)

class CloudViewModel(application: Application) : AndroidViewModel(application) {
    private val repository: CloudRepository
    
    // UI state streams from Room Database
    val accounts: StateFlow<List<CloudAccount>>
    val resources: StateFlow<List<DiscoveryResource>>
    val savedMigrations: StateFlow<List<SavedMigration>>

    // FastAPI Backend Controls & Sync Configurations
    private val _useBackend = MutableStateFlow(true)
    val useBackend = _useBackend.asStateFlow()

    private val _isBackendConnected = MutableStateFlow(false)
    val isBackendConnected = _isBackendConnected.asStateFlow()

    // SRE Portal user authentication & organization state flows
    private val _currentUserEmail = MutableStateFlow<String?>("admin@cloudops.ai")
    val currentUserEmail = _currentUserEmail.asStateFlow()

    private val _currentOrgName = MutableStateFlow<String?>("Mumbai Operations Center")
    val currentOrgName = _currentOrgName.asStateFlow()

    private val _currentOrgId = MutableStateFlow<Int?>(1)
    val currentOrgId = _currentOrgId.asStateFlow()

    private val _currentOrgPlan = MutableStateFlow<String?>("PRO_ENTERPRISE_SRE")
    val currentOrgPlan = _currentOrgPlan.asStateFlow()

    private val _jwtToken = MutableStateFlow<String?>(null)
    val jwtToken = _jwtToken.asStateFlow()

    private val _currentUserRole = MutableStateFlow<String?>("SUPER_ADMIN")
    val currentUserRole = _currentUserRole.asStateFlow()

    private val _selectedRegion = MutableStateFlow("ap-south-1")
    val selectedRegion = _selectedRegion.asStateFlow()

    private val _regions = MutableStateFlow<List<com.example.api.AwsRegion>>(emptyList())
    val regions = _regions.asStateFlow()

    fun updateSelectedRegion(region: String) {
        _selectedRegion.value = region
        com.example.api.TokenStorage.selectedRegion = region
        try {
            com.example.api.SecureStorage.saveSelectedRegion(getApplication(), region)
        } catch (e: Exception) {
            Log.e("CloudViewModel", "Failed to save selected region: ${e.message}")
        }
        refreshAllFeeds()
    }

    fun loadRegions() {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value) {
                    val apiService = com.example.api.CloudOpsBackendClient.service
                    val response = apiService.getRegions()
                    if (response.success && response.regions.isNotEmpty()) {
                        _regions.emit(response.regions)
                        Log.e("REGION_DEBUG", "Loaded ${response.regions.size} regions")
                        response.regions.forEach {
                            Log.e("REGION_DEBUG", "Region: ${it.name}")
                        }
                    } else {
                        Log.e("CloudViewModel", "Backend API returned success = ${response.success} or of empty size")
                    }
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Failed to load regions from backend: ${e.message}")
            }
        }
    }

    fun loadRegionsForAccount(accountId: Int) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                val apiService = com.example.api.CloudOpsBackendClient.service
                val response = apiService.getAccountRegions(accountId)
                if (response.success && response.regions.isNotEmpty()) {
                    _regions.emit(response.regions)
                }
            } catch (e: Exception) {
                Log.e("REGION_ERROR", "Account region load failed: ${e.message}")
            }
        }
    }

    private fun getOfflineRegions(): List<com.example.api.AwsRegion> {
        return listOf(
            com.example.api.AwsRegion("ap-south-1", "ec2.ap-south-1.amazonaws.com"),
            com.example.api.AwsRegion("us-east-1", "ec2.us-east-1.amazonaws.com"),
            com.example.api.AwsRegion("ap-southeast-1", "ec2.ap-southeast-1.amazonaws.com"),
            com.example.api.AwsRegion("eu-central-1", "ec2.eu-central-1.amazonaws.com"),
            com.example.api.AwsRegion("ap-northeast-1", "ec2.ap-northeast-1.amazonaws.com"),
            com.example.api.AwsRegion("ap-northeast-2", "ec2.ap-northeast-2.amazonaws.com"),
            com.example.api.AwsRegion("ap-northeast-3", "ec2.ap-northeast-3.amazonaws.com"),
            com.example.api.AwsRegion("ca-central-1", "ec2.ca-central-1.amazonaws.com"),
            com.example.api.AwsRegion("eu-west-1", "ec2.eu-west-1.amazonaws.com"),
            com.example.api.AwsRegion("eu-west-2", "ec2.eu-west-2.amazonaws.com"),
            com.example.api.AwsRegion("eu-west-3", "ec2.eu-west-3.amazonaws.com"),
            com.example.api.AwsRegion("us-west-1", "ec2.us-west-1.amazonaws.com"),
            com.example.api.AwsRegion("us-west-2", "ec2.us-west-2.amazonaws.com")
        )
    }

    private val _showEc2Resources = MutableStateFlow(false)
    val showEc2Resources = _showEc2Resources.asStateFlow()

    fun setShowEc2Resources(show: Boolean) {
        _showEc2Resources.value = show
    }

    private val _lastTemporaryCredentials = MutableStateFlow<com.example.api.TemporaryCredentialsResponse?>(null)
    val lastTemporaryCredentials = _lastTemporaryCredentials.asStateFlow()

    private val _costSummary = MutableStateFlow<com.example.api.CloudCostSummary?>(null)
    val costSummary = _costSummary.asStateFlow()

    private val _optimizationRecommendations = MutableStateFlow<List<com.example.api.RecommendationItem>>(emptyList())
    val optimizationRecommendations = _optimizationRecommendations.asStateFlow()

    private val _optimizationSavings = MutableStateFlow<com.example.api.OptimizationSavings?>(null)
    val optimizationSavings = _optimizationSavings.asStateFlow()

    private val _aiInsights = MutableStateFlow<com.example.api.AIInsightsResponse?>(null)
    val aiInsights = _aiInsights.asStateFlow()

    private val _resourceSummary = MutableStateFlow<com.example.api.ResourceSummary?>(null)
    val resourceSummary = _resourceSummary.asStateFlow()

    private val _graphTopology = MutableStateFlow<com.example.api.GraphResponse?>(null)
    val graphTopology = _graphTopology.asStateFlow()

    private val _topologyCategories = MutableStateFlow<List<com.example.api.TopologyCategory>>(emptyList())
    val topologyCategories = _topologyCategories.asStateFlow()

    private val _topologyResources = MutableStateFlow<List<com.example.api.TopologyResource>>(emptyList())
    val topologyResources = _topologyResources.asStateFlow()

    private val _topologyLevel3 = MutableStateFlow<com.example.api.TopologyLevel3Response?>(null)
    val topologyLevel3 = _topologyLevel3.asStateFlow()

    private val _resourceGraph = MutableStateFlow<com.example.api.ResourceGraphResponse?>(null)
    val resourceGraph = _resourceGraph.asStateFlow()

    private val _currentTopologyCategory = MutableStateFlow<String?>(null)
    val currentTopologyCategory = _currentTopologyCategory.asStateFlow()

    private val _currentTopologyResourceId = MutableStateFlow<String?>(null)
    val currentTopologyResourceId = _currentTopologyResourceId.asStateFlow()

    // Local runtime states
    private val _isDiscovering = MutableStateFlow(false)
    val isDiscovering = _isDiscovering.asStateFlow()

    private val _discoveryOutputLogs = MutableStateFlow<List<String>>(emptyList())
    val discoveryOutputLogs = _discoveryOutputLogs.asStateFlow()

    private val _activeJobs = MutableStateFlow<List<BackgroundJob>>(emptyList())
    val activeJobs = _activeJobs.asStateFlow()

    // Incident management states
    private val _incidents = MutableStateFlow<List<CloudIncident>>(emptyList())
    val incidents = _incidents.asStateFlow()

    private val _healActions = MutableStateFlow<List<SelfHealAction>>(emptyList())
    val healActions = _healActions.asStateFlow()

    // Dependency Graph states
    private val _selectedGraphNode = MutableStateFlow<DiscoveryResource?>(null)
    val selectedGraphNode = _selectedGraphNode.asStateFlow()

    // Gemini AI Chat states
    private val _chatMessages = MutableStateFlow<List<ChatMessage>>(
        listOf(
            ChatMessage(
                text = "Hello! I am your Multi-Cloud Intelligence & Migration Advisor.\n" +
                        "I can automatically analyze your cloud topology, run cost optimizations, audit firewall risks, or write secure Terraform configurations. What do you want to explore today?",
                isUser = false
            )
        )
    )
    val chatMessages = _chatMessages.asStateFlow()

    private val _isGeneratingAi = MutableStateFlow(false)
    val isGeneratingAi = _isGeneratingAi.asStateFlow()

    // Terraform Generator States
    private val _sourceCloud = MutableStateFlow("AWS")
    val sourceCloud = _sourceCloud.asStateFlow()

    private val _targetCloud = MutableStateFlow("Azure")
    val targetCloud = _targetCloud.asStateFlow()

    private val _selectedServices = MutableStateFlow<Set<String>>(
        setOf("Compute (EC2/VM)", "Database (RDS/SQL)", "Storage (S3/Blob)")
    )
    val selectedServices = _selectedServices.asStateFlow()

    private val _generatedTerraform = MutableStateFlow("")
    val generatedTerraform = _generatedTerraform.asStateFlow()

    private val _isGeneratingTerraform = MutableStateFlow(false)
    val isGeneratingTerraform = _isGeneratingTerraform.asStateFlow()

    init {
        val database = CloudDatabase.getDatabase(application)
        repository = CloudRepository(database.dao)

        accounts = repository.allAccounts.stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

        resources = repository.allResources.stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

        savedMigrations = repository.allSavedMigrations.stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

        // Seed initial data so the user has beautiful instant visualization
        _costSummary.value = null
        seedInitialDatabaseData()

        // Load custom backend URL from secure storage if set
        try {
            val savedUrl = com.example.api.SecureStorage.getCustomBaseUrl(application)
            if (savedUrl != null) {
                com.example.api.CloudOpsBackendClient.setCustomBaseUrl(savedUrl)
                Log.i("CloudViewModel", "Successfully loaded persistent custom backend URL: $savedUrl")
            }
        } catch (e: java.lang.Exception) {
            Log.e("CloudViewModel", "Failed to restore custom backend URL: ${e.message}")
        }

        // Persistent Session Restoration via Hardware AES-KeyStore Vault
        try {
            val recovered = com.example.api.SecureStorage.restoreSession(application)
            if (recovered != null) {
                _jwtToken.value = recovered.accessToken
                _currentUserEmail.value = recovered.email
                _currentOrgName.value = recovered.orgName
                _currentOrgId.value = recovered.orgId
                _currentOrgPlan.value = recovered.plan
                _currentUserRole.value = recovered.role
                Log.i("CloudViewModel", "Successfully restored SRE operator profile from secure storage: ${recovered.email}")
            }
        } catch (e: Exception) {
            Log.e("CloudViewModel", "Secure storage session automatic recovery failed: ${e.message}")
        }

        // Restoration of saved AWS Selected Region
        try {
            val savedRegion = com.example.api.SecureStorage.getSelectedRegion(application)
            _selectedRegion.value = savedRegion
            com.example.api.TokenStorage.selectedRegion = savedRegion
        } catch (e: Exception) {
            Log.e("CloudViewModel", "Failed to restore selected region: ${e.message}")
        }

        // Initialize with real regions immediately so that the dropdown works and is functional right away
        _regions.value = getOfflineRegions()

        // Fetch dynamic cloud regions
        loadRegions()

        // Sync and refresh from local FastAPI SRE backend on launch (run once at start)
        viewModelScope.launch(Dispatchers.IO) {
            try {
                refreshAllFeeds()
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Initial sync failed: ${e.message}")
            }
        }
    }

    /**
     * Toggles whether the app delegates operations to the Python FastAPI backend
     * or runs completely inside local Room database mock scopes for offline previews.
     */
    fun setUseBackend(enabled: Boolean) {
        _useBackend.value = enabled
        refreshAllFeeds()
    }

    /**
     * Triggers manual database/API refresh.
     */
    fun manualRefresh() {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                refreshAllFeeds()
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Manual refresh failed", e)
            }
        }
    }

    /**
     * Updates and persists custom live EC2 backend address dynamically.
     */
    fun updateBackendUrl(url: String) {
        try {
            com.example.api.SecureStorage.saveCustomBaseUrl(getApplication(), url.trim())
            com.example.api.CloudOpsBackendClient.setCustomBaseUrl(url.trim())
            Log.i("CloudViewModel", "Configured and saved new live gateway IP/URL: $url")
            refreshAllFeeds()
        } catch (e: Exception) {
            Log.e("CloudViewModel", "Failed to save backend URL custom configuration: ${e.message}")
        }
    }

    /**
     * Attempts to read live cloud accounts, discovered resources, and DevSecOps warning
     * incidents directly from the FastAPI REST server.
     */
    fun refreshAllFeeds() {
        viewModelScope.launch(Dispatchers.IO) {
            if (!_useBackend.value) {
                _isBackendConnected.value = false
                return@launch
            }
            try {
                Log.i("CloudViewModel", "Attempting backend sync with url: ${com.example.api.CloudOpsBackendClient.baseUrl}")
                val apiService = com.example.api.CloudOpsBackendClient.service
                
                // Fetch dynamic cloud regions
                try {
                    val response = apiService.getRegions()
                    if (response.success && response.regions.isNotEmpty()) {
                        _regions.emit(response.regions)
                    }
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "Failed to fetch regions during sync: ${e.message}")
                }

                // Fetch accounts and sync with local Room
                val remoteAccounts = apiService.getAccounts()
                repository.clearAccounts()
                repository.insertAccounts(remoteAccounts)
                _isBackendConnected.value = true
                Log.i("CloudViewModel", "Successfully connected to FastAPI. Synced accounts.")

                // Sync remote resources with local Room to keep everything in sync
                try {
                    val remoteResources = apiService.getResources()
                    repository.clearResources()
                    repository.insertResources(remoteResources)
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "Failed to sync remote resources: ${e.message}")
                }

                try {
                    _resourceSummary.value = apiService.getResourcesSummary()
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "Failed to fetch resource summary: ${e.message}")
                }

                try {
                    _graphTopology.value = apiService.getGraph()
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "Failed to fetch graph topology: ${e.message}")
                }

                try {
                    _topologyCategories.value = apiService.getTopologySummary()
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "Failed to fetch topology level 1: ${e.message}")
                }

                // Fetch Cost Explorer Summary statistics
                try {
                    val remoteCost = apiService.getCostSummary()
                    _costSummary.value = remoteCost
                } catch (ceError: Exception) {
                    Log.e("CloudViewModel", "Failed to fetch Cost Explorer billing details from REST gateway: ${ceError.message}")
                }

                // Fetch dynamic cloud optimization results (Phase 6)
                try {
                    val remoteOps = apiService.getOptimizationRecommendations()
                    _optimizationRecommendations.value = remoteOps
                } catch (ce: Exception) {
                    Log.e("CloudViewModel", "Failed to fetch cloud optimizations: ${ce.message}")
                }

                try {
                    val remoteSavings = apiService.getOptimizationSavings()
                    _optimizationSavings.value = remoteSavings
                } catch (ce: Exception) {
                    Log.e("CloudViewModel", "Failed to fetch cloud savings: ${ce.message}")
                }

                // Fetch live generative Gemini intelligence reports (Phase 7)
                try {
                    val remoteAI = apiService.getAIInsights()
                    _aiInsights.value = remoteAI
                } catch (ce: Exception) {
                    Log.e("CloudViewModel", "Failed to fetch generative AI insights: ${ce.message}")
                }

                // Populate live scanned incidents from PostgreSQL/Boto3 scan
                val remoteIncidents = apiService.getIncidents()
                _incidents.value = remoteIncidents
            } catch (e: Exception) {
                _isBackendConnected.value = false
                Log.w("CloudViewModel", "Local FastAPI server not reachable. Running on high-performance Room fallback. Details: ${e.message}")
            }
        }
    }

    private fun seedInitialDatabaseData() {
        viewModelScope.launch(Dispatchers.IO) {
            // Check if incidents exist; if not, populate demo incidents
            if (_incidents.value.isEmpty()) {
                _incidents.value = listOf(
                    CloudIncident(
                        id = "inc-01",
                        title = "Critical CPU Spike on Web clusters",
                        severity = "CRITICAL",
                        resourceId = "app-web-servers",
                        description = "FastAPI web server nodes ('app-web-servers') are experiencing an anomalous memory leak and CPU spike. CPU utilization is reaching 98.4%. Scaler limit warning.",
                        status = "ACTIVE"
                    ),
                    CloudIncident(
                        id = "inc-02",
                        title = "Wildcard SSH Security Group Open",
                        severity = "WARNING",
                        resourceId = "vpc-09ab02c",
                        description = "Port 22 SSH ingress open to entire internet ('0.0.0.0/0') within 'Main-Corporate-Net' resource group 'sg-web-public'.",
                        status = "ACTIVE"
                    ),
                    CloudIncident(
                        id = "inc-03",
                        title = "Storage Blob Archive Unencrypted",
                        severity = "WARNING",
                        resourceId = "s3-corporate-archive",
                        description = "Audit scans found that AWS object bucket 's3-corporate-archive-992' contains 14.2TB of archive logs without default KMS encryption tags.",
                        status = "ACTIVE"
                    )
                )
            }

            // Check if accounts exist; if not, populate demo configurations
            accounts.take(1).collect { list ->
                if (list.isEmpty()) {
                    repository.insertAccount(
                        CloudAccount(
                            provider = "AWS",
                            name = "AWS Corporate Production",
                            credentialsHint = "Role: arn:aws:iam::119027251070:role/CloudMigrateRole",
                            region = "us-east-1"
                        )
                    )
                    repository.insertAccount(
                        CloudAccount(
                            provider = "Azure",
                            name = "Azure Enterprise Dev-Sandbox",
                            credentialsHint = "Tenant ID: 9fcd-1234-58bc-fa39",
                            region = "eastus"
                        )
                    )
                }
            }

            // Seed initial completed migration
            savedMigrations.take(1).collect { list ->
                if (list.isEmpty()) {
                    repository.saveMigration(
                        SavedMigration(
                            title = "Core Web Server Migration (AWS to Azure)",
                            sourceCloud = "AWS",
                            targetCloud = "Azure",
                            servicesMigrated = "Compute, Database, Storage, Networking",
                            terraformCode = """
                            # Produced by CloudMigrate Platform
                            
                            provider "azurerm" {
                              features {}
                            }
                            
                            resource "azurerm_resource_group" "rg" {
                              name     = "cloudmigrate-app-rg"
                              location = "East US"
                            }
                            
                            # VPC migrated to Azure Virtual Network
                            resource "azurerm_virtual_network" "vnet" {
                              name                = "app-vnet"
                              address_space       = ["10.0.0.0/16"]
                              location            = azurerm_resource_group.rg.location
                              resource_group_name = azurerm_resource_group.rg.name
                            }
                            
                            # EC2 migrated to VM
                            resource "azurerm_linux_virtual_machine" "web_nodes" {
                              name                = "fastapi-web"
                              resource_group_name = azurerm_resource_group.rg.name
                              location            = azurerm_resource_group.rg.location
                              size                = "Standard_D2s_v3"
                              admin_username      = "azureuser"
                              network_interface_ids = []
                              
                              os_disk {
                                caching              = "ReadWrite"
                                storage_account_type = "Standard_LRS"
                              }
                            }
                            """.trimIndent()
                        )
                    )
                }
            }
        }
    }

    // --- Graph Interaction ---
    fun selectGraphNode(resource: DiscoveryResource?) {
        _selectedGraphNode.value = resource
    }

    // --- User Authentication Actions ---
    fun registerUser(
        email: String,
        password: String,
        organisation: String,
        plan: String = "BASIC",
        role: String = "ORG_ADMIN",
        onCompleted: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value) {
                    val res = com.example.api.CloudOpsBackendClient.service.register(
                        com.example.api.UserRegisterRequest(email, password, organisation, plan, role)
                    )
                    val finalRole = res.role ?: role
                    _currentUserEmail.value = res.userEmail
                    _currentOrgName.value = res.organizationName
                    _currentOrgId.value = res.organizationId
                    _currentOrgPlan.value = res.plan
                    _jwtToken.value = res.accessToken
                    _currentUserRole.value = finalRole

                    // Save safely in KeyStore encrypted session storage
                    com.example.api.SecureStorage.saveSession(
                        getApplication(),
                        res.accessToken,
                        res.userEmail,
                        res.organizationName,
                        res.organizationId,
                        res.plan,
                        finalRole
                    )

                    onCompleted("Successfully registered SRE control profile for ${res.organizationName}!")
                } else {
                    _currentUserEmail.value = email
                    _currentOrgName.value = organisation
                    _currentOrgId.value = 42
                    _currentOrgPlan.value = plan
                    _jwtToken.value = "jwt_offline_mock"
                    _currentUserRole.value = role

                    com.example.api.SecureStorage.saveSession(
                        getApplication(),
                        "jwt_offline_mock",
                        email,
                        organisation,
                        42,
                        plan,
                        role
                    )

                    onCompleted("Offline registration success! Org context enabled.")
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Register SRE profile failed: ${e.message}")
                onError(e.message ?: "Authentication server timeout")
            }
        }
    }

    fun loginUser(email: String, password: String, onCompleted: (String) -> Unit, onError: (String) -> Unit) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value) {
                    val res = com.example.api.CloudOpsBackendClient.service.login(
                        com.example.api.UserLoginRequest(email, password)
                    )
                    val finalRole = res.role ?: "ORG_ADMIN"
                    _currentUserEmail.value = res.userEmail
                    _currentOrgName.value = res.organizationName
                    _currentOrgId.value = res.organizationId
                    _currentOrgPlan.value = res.plan
                    _jwtToken.value = res.accessToken
                    _currentUserRole.value = finalRole

                    // Save safely in KeyStore encrypted session storage
                    com.example.api.SecureStorage.saveSession(
                        getApplication(),
                        res.accessToken,
                        res.userEmail,
                        res.organizationName,
                        res.organizationId,
                        res.plan,
                        finalRole
                    )

                    onCompleted("Welcome back SRE specialist! Access level: $finalRole")
                } else {
                    _currentUserEmail.value = email
                    _currentOrgName.value = "Local Operations"
                    _currentOrgId.value = 1
                    _currentOrgPlan.value = "ENTERPRISE"
                    _jwtToken.value = "jwt_offline_mock"
                    _currentUserRole.value = "ORG_ADMIN"

                    com.example.api.SecureStorage.saveSession(
                        getApplication(),
                        "jwt_offline_mock",
                        email,
                        "Local Operations",
                        1,
                        "ENTERPRISE",
                        "ORG_ADMIN"
                    )

                    onCompleted("Logged in successfully offline as SRE Operator.")
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Login request failed: ${e.message}")
                onError(e.message ?: "Invalid email or credentials matching")
            }
        }
    }

    fun logoutUser() {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value && _jwtToken.value != null && _jwtToken.value != "jwt_offline_mock") {
                    com.example.api.CloudOpsBackendClient.service.logout()
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Silent server logout notification failed: ${e.message}")
            }
            
            _currentUserEmail.value = "admin@cloudops.ai"
            _currentOrgName.value = "Mumbai Operations Center"
            _currentOrgId.value = 1
            _currentOrgPlan.value = "PRO_ENTERPRISE_SRE"
            _jwtToken.value = null
            _currentUserRole.value = "SUPER_ADMIN"
            _lastTemporaryCredentials.value = null

            // Erase hardware KeyStore secret records
            com.example.api.SecureStorage.clearSession(getApplication())
        }
    }

    // --- Provider-Specific Connect Actions (Federations with STS validation) ---
    fun connectAwsCloud(
        roleArn: String,
        region: String,
        accountName: String,
        onSuccess: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value && _isBackendConnected.value) {
                    val response = com.example.api.CloudOpsBackendClient.service.connectAws(
                        com.example.api.AwsConnectPayload(roleArn, region, accountName)
                    )
                    val account = CloudAccount(
                        provider = "AWS",
                        name = accountName,
                        credentialsHint = "Role: " + roleArn.takeLast(24),
                        region = region
                    )
                    repository.insertAccount(account)
                    refreshAllFeeds()
                    onSuccess("AWS bounded successfully! Temp credentials: ${response.account.accountId}")
                } else {
                    val account = CloudAccount(
                        provider = "AWS",
                        name = accountName,
                        credentialsHint = "Role: " + roleArn.takeLast(24),
                        region = region
                    )
                    repository.insertAccount(account)
                    onSuccess("AWS STS Connection mapped in local database.")
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "AWS Connect integration failed: ${e.message}")
                onError(e.message ?: "Role assumption forbidden or invalid ARN format")
            }
        }
    }

    fun connectAzureCloud(
        tenantId: String,
        clientId: String,
        clientSecret: String,
        region: String,
        accountName: String,
        onSuccess: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value && _isBackendConnected.value) {
                    val response = com.example.api.CloudOpsBackendClient.service.connectAzure(
                        com.example.api.AzureConnectPayload(tenantId, clientId, clientSecret, region, accountName)
                    )
                    val account = CloudAccount(
                        provider = "Azure",
                        name = accountName,
                        credentialsHint = "Tenant: " + tenantId.take(12) + "...",
                        region = region
                    )
                    repository.insertAccount(account)
                    refreshAllFeeds()
                    onSuccess("Azure Subscription connected! Session established.")
                } else {
                    val account = CloudAccount(
                        provider = "Azure",
                        name = accountName,
                        credentialsHint = "Tenant: " + tenantId.take(12),
                        region = region
                    )
                    repository.insertAccount(account)
                    onSuccess("Azure federation mapped locally.")
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Azure Service Principal authentication failed: ${e.message}")
                onError(e.message ?: "Client Secret unauthorized")
            }
        }
    }

    fun connectGcpCloud(
        serviceAccountJson: String,
        region: String,
        accountName: String,
        onSuccess: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value && _isBackendConnected.value) {
                    val response = com.example.api.CloudOpsBackendClient.service.connectGcp(
                        com.example.api.GcpConnectPayload(serviceAccountJson, region, accountName)
                    )
                    val account = CloudAccount(
                        provider = "GCP",
                        name = accountName,
                        credentialsHint = "Service Account Keystore",
                        region = region
                    )
                    repository.insertAccount(account)
                    refreshAllFeeds()
                    onSuccess("GCP connected via OAuth2! Multi-cloud control plane synchronized.")
                } else {
                    val account = CloudAccount(
                        provider = "GCP",
                        name = accountName,
                        credentialsHint = "SA Private Key",
                        region = region
                    )
                    repository.insertAccount(account)
                    onSuccess("GCP Service Account linked locally.")
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "GCP Service Account validation failed: ${e.message}")
                onError(e.message ?: "Invalid private JSON key")
            }
        }
    }

    fun fetchTemporalCredentialsDetails(accountId: Int, onComplete: () -> Unit = {}) {
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value && _isBackendConnected.value) {
                    val details = com.example.api.CloudOpsBackendClient.service.getTemporaryCredentials(accountId)
                    _lastTemporaryCredentials.value = details
                    onComplete()
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Could not fetch temporal credentials: ${e.message}")
            }
        }
    }

    // --- Account Forms ---
    fun addCloudAccount(provider: String, name: String, credentialsHint: String, region: String) {
        viewModelScope.launch(Dispatchers.IO) {
            val account = CloudAccount(
                provider = provider,
                name = name,
                credentialsHint = credentialsHint,
                region = region
            )
            repository.insertAccount(account)

            if (_useBackend.value && _isBackendConnected.value) {
                try {
                    com.example.api.CloudOpsBackendClient.service.addAccount(account)
                    refreshAllFeeds()
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "Error syncing new cloud account with FastAPI: ${e.message}")
                }
            }
        }
    }

    fun removeCloudAccount(id: Int) {
        viewModelScope.launch(Dispatchers.IO) {
            repository.deleteAccount(id)

            if (_useBackend.value && _isBackendConnected.value) {
                try {
                    com.example.api.CloudOpsBackendClient.service.deleteAccount(id)
                    refreshAllFeeds()
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "Error deleting cloud account from FastAPI: ${e.message}")
                }
            }
        }
    }

    // --- AI Chat Actions ---
    fun sendChatMessage(text: String) {
        if (text.trim().isEmpty()) return
        
        val userMsg = ChatMessage(text = text, isUser = true)
        _chatMessages.update { it + userMsg }

        _isGeneratingAi.value = true
        viewModelScope.launch {
            if (_useBackend.value && _isBackendConnected.value) {
                try {
                    val response = com.example.api.CloudOpsBackendClient.service.getAICopilotResponse(
                        com.example.api.AIChatPayload(text)
                    )
                    _chatMessages.update {
                        it + ChatMessage(text = response.response, isUser = false)
                    }
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "FastAPI Copilot connection failed: ${e.message}")
                    fallbackToLocalGemini(text)
                }
            } else {
                fallbackToLocalGemini(text)
            }
            _isGeneratingAi.value = false
        }
    }

    private suspend fun fallbackToLocalGemini(text: String) {
        val systemInstruction = "You are an intelligent, senior multi-cloud migration and dependency analysis architect. Your goal is to guide developers on Cloudamize-grade topology diagrams, cost models, IAM vulnerabilities, and target deployments. Provide rich, highly structured, technical feedback utilizing Markdown schemas."
        val apiResponse = GeminiClient.generateMigrationFeedback(
            prompt = text,
            systemInstruction = systemInstruction
        )
        _chatMessages.update {
            it + ChatMessage(text = apiResponse, isUser = false)
        }
    }

    fun submitPresetQuery(query: String) {
        sendChatMessage(query)
    }

    fun loadTopologyCategory(category: String) {
        _currentTopologyCategory.value = category
        _currentTopologyResourceId.value = null
        _topologyLevel3.value = null
        _resourceGraph.value = null
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value) {
                    val apiService = com.example.api.CloudOpsBackendClient.service
                    _topologyResources.value = apiService.getTopologyResources(category)
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Failed to fetch topology resources: ${e.message}")
            }
        }
    }

    fun loadTopologyResource(resourceId: String) {
        _currentTopologyResourceId.value = resourceId
        viewModelScope.launch(Dispatchers.IO) {
            try {
                if (_useBackend.value) {
                    val apiService = com.example.api.CloudOpsBackendClient.service
                    _topologyLevel3.value = apiService.getTopologyLevel3(resourceId)
                    _resourceGraph.value = apiService.getResourceGraph(resourceId)
                }
            } catch (e: Exception) {
                Log.e("CloudViewModel", "Failed to fetch topology level 3 or graph: ${e.message}")
            }
        }
    }

    fun clearTopologySelection() {
        if (_currentTopologyResourceId.value != null) {
            _currentTopologyResourceId.value = null
            _topologyLevel3.value = null
            _resourceGraph.value = null
        } else if (_currentTopologyCategory.value != null) {
            _currentTopologyCategory.value = null
            _topologyResources.value = emptyList()
        }
    }

    // --- Core Discovery Worker Simulation & Polling Engine ---
    fun startCloudDiscovery() {
        if (_isDiscovering.value) return
        _isDiscovering.value = true
        _discoveryOutputLogs.value = emptyList()

        viewModelScope.launch {
            if (_useBackend.value && _isBackendConnected.value) {
                // RUN LIVE DISCOVERY ON FASTAPI BACKEND
                _discoveryOutputLogs.update { it + "📡 Conn establish: dispatching SRE Discovery probe to remote FastAPI instance..." }
                try {
                    val apiService = com.example.api.CloudOpsBackendClient.service
                    val remoteJob = apiService.triggerDiscovery("AWS")
                    
                    _activeJobs.update { it + remoteJob }
                    _discoveryOutputLogs.update { it + "⚙️ Daemon Active: task [id=${remoteJob.id}] queued successfully in server pool." }

                    var progress = 0.0f
                    var status = "QUEUED"
                    
                    // Poll FastAPI for real-time progress updates matching asynchronous Celery workers
                    while (status == "RUNNING" || status == "QUEUED") {
                        delay(1200)
                        try {
                            val updatedJob = apiService.getJobDetails(remoteJob.id)
                            progress = updatedJob.progress
                            status = updatedJob.status
                            
                            // Log dynamic server progress ratios
                            _discoveryOutputLogs.update { current ->
                                current + "📊 Sync Engine: Server Scan Progress reaches ${(progress * 100).toInt()}%..."
                            }

                            // Update active jobs trace in UI
                            _activeJobs.update { jobs ->
                                jobs.map { j ->
                                    if (j.id == remoteJob.id) updatedJob else j
                                }
                            }
                        } catch (pollEx: Exception) {
                            Log.e("CloudViewModel", "Error polling SRE job details: ${pollEx.message}")
                            status = "FAILED"
                        }
                    }

                    if (status == "COMPLETED") {
                        _discoveryOutputLogs.update { it + "✅ Complete: FastAPI successfully harvested live AWS assets and updated PostgreSQL database." }
                        // Refresh all UI data streams now that the database has updated scan results!
                        refreshAllFeeds()
                    } else {
                        _discoveryOutputLogs.update { it + "❌ Anomaly: SRE scan job reported status = $status." }
                    }
                } catch (apiEx: Exception) {
                    _discoveryOutputLogs.update { it + "⚠️ Network error: could not perform live FastAPI SRE sweep. Falling back to local simulator..." }
                    runLocalDiscoverySimulation()
                }
            } else {
                // Run completely local offline simulation
                runLocalDiscoverySimulation()
            }
            _isDiscovering.value = false
        }
    }

    private suspend fun runLocalDiscoverySimulation() {
        val steps = listOf(
            "Initializing Discovery Worker daemon on Celery task queue... OK",
            "Authenticating with current AWS Access Credentials... Verified",
            "Crawl Phase: Initiating complete topology sweep in regional cluster (us-east-1)...",
            "Graph Map: Scanning active Virtual Private Cloud (vpc-09ab02c) networks...",
            "Graph Map: Found 4 subnets | Port scanning security ingress layers...",
            "WARNING: SSH ingress port 22 is open on 0.0.0.0/0 under security group 'sg-web-public'!",
            "Inventory Caching: Harvesting EC2 configurations... found fastapi-web-cluster nodes.",
            "Inventory Caching: Harvesting RDS details... PostgreSQL on multi-AZ engine authenticated.",
            "Asset Mapping: Scanning unencrypted S3 objects under bucket 's3-corporate-archive-992'...",
            "Harvesting metrics: Mapping AWS Lambda trigger events ➔ SQS ➔ SNS.",
            "Neo4j Integration: Syncing active service topology relationships into dependency visual graphs...",
            "Cost Audit Scanner: Calculating delta values and machine optimization scales...",
            "Success: Multi-Cloud Network Scan successfully logged to Room cache. Ready."
        )

        val discoveryJob = BackgroundJob(
            id = "job-" + UUID.randomUUID().toString().take(6),
            name = "AWS Topology Discovery Engine",
            progress = 0.0f,
            status = "RUNNING"
        )
        _activeJobs.value = _activeJobs.value + discoveryJob

        for (i in steps.indices) {
            delay(500)
            _discoveryOutputLogs.update { it + steps[i] }
            
            val currentProgress = (i + 1).toFloat() / steps.size
            _activeJobs.update { jobs ->
                jobs.map { job ->
                    if (job.id == discoveryJob.id) {
                        job.copy(
                            progress = currentProgress,
                            status = if (i == steps.size - 1) "COMPLETED" else "RUNNING"
                        )
                    } else job
                }
            }
        }

    }

    // --- Terraform Generator Settings ---
    fun setSourceCloud(cloud: String) {
        _sourceCloud.value = cloud
    }

    fun setTargetCloud(cloud: String) {
        _targetCloud.value = cloud
    }

    fun toggleServiceSelected(service: String) {
        _selectedServices.update { current ->
            if (current.contains(service)) {
                current.minus(service)
            } else {
                current.plus(service)
            }
        }
    }

    fun runTerraformGenerator() {
        if (_isGeneratingTerraform.value) return
        _isGeneratingTerraform.value = true
        _generatedTerraform.value = ""

        viewModelScope.launch {
            // Trigger a simulated celery job for Terraform compiler
            val tfJob = BackgroundJob(
                id = "job-" + UUID.randomUUID().toString().take(6),
                name = "Terraform Code Generator Service",
                progress = 0.1f,
                status = "RUNNING"
            )
            _activeJobs.update { it + tfJob }

            delay(1200)

            _activeJobs.update { jobs ->
                jobs.map { j ->
                    if (j.id == tfJob.id) j.copy(progress = 0.6f) else j
                }
            }

            // Let's call Gemini if key is set or generate rich formatted template
            val prompt = """
                Generate complete, valid, structured and secure Terraform code for migrating an enterprise environment from ${_sourceCloud.value} to ${_targetCloud.value}.
                Migrate the following active modules: ${_selectedServices.value.joinToString(", ")}.
                Specify standard multi-cloud resource conversions, variables, and provider specifications.
            """.trimIndent()

            val response = GeminiClient.generateMigrationFeedback(prompt)
            _generatedTerraform.value = response

            _activeJobs.update { jobs ->
                jobs.map { j ->
                    if (j.id == tfJob.id) j.copy(progress = 1.0f, status = "COMPLETED") else j
                }
            }
            _isGeneratingTerraform.value = false
        }
    }

    fun saveGeneratedMigration(title: String) {
        val code = _generatedTerraform.value
        if (code.isEmpty()) return

        viewModelScope.launch(Dispatchers.IO) {
            val mig = SavedMigration(
                title = title,
                sourceCloud = _sourceCloud.value,
                targetCloud = _targetCloud.value,
                servicesMigrated = _selectedServices.value.joinToString(", "),
                terraformCode = code
            )
            repository.saveMigration(mig)
        }
    }

    fun deleteMigration(id: Int) {
        viewModelScope.launch(Dispatchers.IO) {
            repository.deleteMigration(id)
        }
    }

    fun clearTelemetryHistory() {
        _activeJobs.value = emptyList()
    }

    // --- AI Doctor Diagnostic and Self-Healing Engine ---
    fun diagnoseIncident(incident: CloudIncident) {
        _isGeneratingAi.value = true
        
        // Append a diagnostic query into the chat log feeds so the user can see it
        val userQueryMsg = ChatMessage(
            text = "AI DOCTOR DIAGNOSIS REQUEST: Analyze incident '${incident.title}' (${incident.id}) on resource '${incident.resourceId}'",
            isUser = true
        )
        _chatMessages.update { it + userQueryMsg }

        viewModelScope.launch {
            val systemInstruction = "You are a senior DevOps SRE and multi-cloud systems debugger. Identify root cause, proposed fix, risk metrics, and cost/impact score."
            val customPrompt = """
                Conduct a deep-dive diagnosis for:
                Incident ID: ${incident.id}
                Title: ${incident.title}
                Resource ID: ${incident.resourceId}
                Severity: ${incident.severity}
                Description: ${incident.description}
                
                Please return a structured diagnosis in markdown:
                ### DevSecOps Threat Diagnosis
                Identify the root cause of the anomaly.
                
                ### Self-Healing Autonomic Suggestion
                1. Point out step-by-step healing maneuvers.
                2. Explicitly outline recommended corrective scripting.
                
                ### Performance & Posture Score
                Provide a risk metric between 1 and 10, and additional post-remediation billing optimizations.
            """.trimIndent()

            val response = GeminiClient.generateMigrationFeedback(customPrompt, systemInstruction)
            
            _chatMessages.update {
                it + ChatMessage(text = response, isUser = false)
            }
            _isGeneratingAi.value = false
        }
    }

    fun executeSelfHeal(incidentId: String) {
        val incident = _incidents.value.find { it.id == incidentId } ?: return
        if (incident.status != "ACTIVE") return

        // Update status to HEALING
        _incidents.update { list ->
            list.map { inc ->
                if (inc.id == incidentId) inc.copy(status = "HEALING") else inc
            }
        }

        viewModelScope.launch {
            if (_useBackend.value && _isBackendConnected.value) {
                _discoveryOutputLogs.update { it + "🤖 [Self-Heal] Initiating programmatic healing sequence on FastAPI REST client..." }
                try {
                    val response = com.example.api.CloudOpsBackendClient.service.executeSelfHeal(incidentId)
                    
                    response.logs.forEach { logLine ->
                        _discoveryOutputLogs.update { it + "🤖 [Self-Heal] $logLine" }
                        delay(400)
                    }

                    _incidents.update { list ->
                        list.map { inc ->
                            if (inc.id == incidentId) inc.copy(status = response.incidentStatus) else inc
                        }
                    }

                    _healActions.update { actions ->
                        actions + SelfHealAction(
                            id = "act-" + UUID.randomUUID().toString().take(6),
                            incidentId = incidentId,
                            actionName = "autonomic_mitigation_remedy",
                            status = if (response.status == "SUCCESS") "SUCCESS" else "FAILED"
                        )
                    }
                    
                    refreshAllFeeds()
                } catch (e: Exception) {
                    _discoveryOutputLogs.update { it + "⚠️ Healing failed: FastAPI service threw network error: ${e.message}" }
                    _incidents.update { list ->
                        list.map { inc ->
                            if (inc.id == incidentId) inc.copy(status = "ACTIVE") else inc
                        }
                    }
                }
            } else {
                runLocalSelfHealSimulation(incidentId)
            }
        }
    }

    private suspend fun runLocalSelfHealSimulation(incidentId: String) {
        val taskName = when (incidentId) {
            "inc-01" -> "Scale Replica Group | Restart Kubernetes Services"
            "inc-02" -> "IAM Boundaries Restructure | Restrict Port 22 Wildcard"
            "inc-03" -> "SSE-KMS Encryption Policy Ingestion Flow"
            else -> "Kubernetes Pod Repair Daemon task"
        }

        val healJob = BackgroundJob(
            id = "heal-" + UUID.randomUUID().toString().take(6),
            name = "Self-Healing Engine: $taskName",
            progress = 0.0f,
            status = "RUNNING"
        )
        _activeJobs.update { it + healJob }

        val stages = when (incidentId) {
            "inc-01" -> listOf(
                "Autonomic daemon: intercepting CPU critical spike on 'app-web-servers'... OK",
                "Acquiring telemetry metrics... 98.4% CPU cluster load confirmed.",
                "Provisioning 2 additional fastapi replica pods in regional cluster... OK",
                "Redistributing Ingress ALB loads with weighted routing tags... Safe",
                "Performing service restart on m5.large instances... OK",
                "Success: Web clusters stabilized. CPU returned to 24.2%. Status: Healthy."
            )
            "inc-02" -> listOf(
                "Autonomic daemon: auditing security group ports on 'vpc-09ab02c'... OK",
                "Found SSH port 22 open on wide wildcard '0.0.0.0/0'!",
                "Compiling ingress firewall rules... targeting 'sg-web-public' default rules.",
                "Executing IAM boundary restrict script with STS client permissions... OK",
                "Restricted ingress port 22 to specific secure bastion CIDR IP space... OK",
                "Success: Security group secured. wildcards revoked. Status: Secured."
            )
            "inc-03" -> listOf(
                "Autonomic daemon: inspecting encryption configurations on S3 bucket 's3-corporate-archive-992'... OK",
                "Detected raw unencrypted storage logs (14.2TB volume) leaks alert.",
                "Synthesizing KMS secure CMK cluster resources... OK",
                "Applying bucket policy requiring AWS:kms key encryption for write-actions... OK",
                "Triggering background SSE-KMS encrypt scan on ancestral objects... OK",
                "Success: S3 storage bucket fully encrypted in transit and at rest. Status: Secure."
            )
            else -> listOf(
                "Initiating local self-healing job...",
                "Applying default mitigations...",
                "Success: System healed."
            )
        }

        for (i in stages.indices) {
            delay(500)
            _discoveryOutputLogs.update { it + "🤖 [Self-Heal] ${stages[i]}" }

            val currentProgress = (i + 1).toFloat() / stages.size
            _activeJobs.update { jobs ->
                jobs.map { j ->
                    if (j.id == healJob.id) {
                        j.copy(
                            progress = currentProgress,
                            status = if (i == stages.size - 1) "COMPLETED" else "RUNNING"
                        )
                    } else j
                }
            }
        }

        _healActions.update { actions ->
            actions + SelfHealAction(
                id = "act-" + UUID.randomUUID().toString().take(6),
                incidentId = incidentId,
                actionName = taskName,
                status = "SUCCESS"
            )
        }

        _incidents.update { list ->
            list.map { inc ->
                if (inc.id == incidentId) inc.copy(status = "RESOLVED") else inc
            }
        }
    }

    fun resetIncidents() {
        viewModelScope.launch {
            if (_useBackend.value && _isBackendConnected.value) {
                try {
                    com.example.api.CloudOpsBackendClient.service.resetIncidents()
                    refreshAllFeeds()
                } catch (e: Exception) {
                    Log.e("CloudViewModel", "Failed to reset incidents on backend: ${e.message}")
                }
            } else {
                runLocalResetIncidents()
            }
        }
    }

    private fun runLocalResetIncidents() {
        _incidents.value = listOf(
            CloudIncident(
                id = "inc-01",
                title = "Critical CPU Spike on Web clusters",
                severity = "CRITICAL",
                resourceId = "app-web-servers",
                description = "FastAPI web server nodes ('app-web-servers') are experiencing an anomalous memory leak and CPU spike. CPU utilization is reaching 98.4%. Scaler limit warning.",
                status = "ACTIVE"
            ),
            CloudIncident(
                id = "inc-02",
                title = "Wildcard SSH Security Group Open",
                severity = "WARNING",
                resourceId = "vpc-09ab02c",
                description = "Port 22 SSH ingress open to entire internet ('0.0.0.0/0') within 'Main-Corporate-Net' resource group 'sg-web-public'.",
                status = "ACTIVE"
            ),
            CloudIncident(
                id = "inc-03",
                title = "Storage Blob Archive Unencrypted",
                severity = "WARNING",
                resourceId = "s3-corporate-archive",
                description = "Audit scans found that AWS object bucket 's3-corporate-archive-992' contains 14.2TB of archive logs without default KMS encryption tags.",
                status = "ACTIVE"
            )
        )
        _healActions.value = emptyList()
    }

    private fun getDefaultMockCostSummary(): com.example.api.CloudCostSummary {
        return com.example.api.CloudCostSummary(
            month = "",
            actualCost = 0.0,
            forecastCost = 0.0,
            currency = "USD",
            byService = emptyList(),
            dailyTrend = emptyList()
        )
    }
}
