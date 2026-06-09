package com.example.ui.screens

import android.widget.Toast
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.CloudAccount
import com.example.api.TemporaryCredentialsResponse
import com.example.ui.CloudViewModel
import com.example.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CloudConnectorsScreen(
    viewModel: CloudViewModel,
    modifier: Modifier = Modifier
) {
    val accounts by viewModel.accounts.collectAsState()
    val context = LocalContext.current

    // Auth States
    val currentUserEmail by viewModel.currentUserEmail.collectAsState()
    val currentOrgName by viewModel.currentOrgName.collectAsState()
    val currentOrgPlan by viewModel.currentOrgPlan.collectAsState()
    val jwtToken by viewModel.jwtToken.collectAsState()
    val lastTemporaryCredentials by viewModel.lastTemporaryCredentials.collectAsState()

    var isRegisterMode by remember { mutableStateOf(false) }
    var authEmailInput by remember { mutableStateOf("") }
    var authPasswordInput by remember { mutableStateOf("") }
    var authOrgNameInput by remember { mutableStateOf("") }
    var authOrgPlanInput by remember { mutableStateOf("PREMIUM") }

    // Account link states
    var activeTabAddAccount by remember { mutableStateOf("AWS") }
    var accountNameInput by remember { mutableStateOf("") }
    var regionInput by remember { mutableStateOf("us-east-1") }

    // Form fields
    var awsIamArn by remember { mutableStateOf("") }
    var azureTenantId by remember { mutableStateOf("") }
    var azureClientId by remember { mutableStateOf("") }
    var azureClientSecret by remember { mutableStateOf("") }
    var gcpServiceAccountJson by remember { mutableStateOf("") }

    // Dialog state
    var showCredentialsDialogAccount by remember { mutableStateOf<CloudAccount?>(null) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(BentoBg)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Headers
        item {
            Column {
                Text(
                    text = "SECURE CREDENTIALS & SESSIONS VAULT",
                    color = BentoTextSubtitle,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Cloud Connectors",
                    color = BentoTextDark,
                    fontSize = 26.sp,
                    fontWeight = FontWeight.ExtraBold
                )
            }
        }

        // SRE CONTROL HUB USER PROFILE SECTION
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("sre_auth_card"),
                colors = CardDefaults.cardColors(containerColor = if (currentUserEmail != null) Color(0xFFF3EFFF) else Color.White),
                border = BorderStroke(1.dp, if (currentUserEmail != null) BentoPurplePrimary.copy(alpha = 0.5f) else BentoBorderMedium),
                shape = RoundedCornerShape(24.dp)
            ) {
                Column(modifier = Modifier.padding(18.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            modifier = Modifier.size(36.dp),
                            shape = RoundedCornerShape(10.dp),
                            color = BentoPurplePrimary
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    imageVector = if (currentUserEmail != null) Icons.Default.VerifiedUser else Icons.Default.AdminPanelSettings,
                                    contentDescription = null,
                                    tint = Color.White,
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(
                                text = "SRE ORGANIZATIONAL HUB",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoTextSubtitle,
                                fontFamily = FontFamily.Monospace
                            )
                            Text(
                                text = if (currentUserEmail != null) "Control Plane Active" else "Authenticate Workspace Engine",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.ExtraBold,
                                color = BentoTextDark
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    if (currentUserEmail != null) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(14.dp))
                                .background(Color.White)
                                .border(1.dp, BentoBorderLight, RoundedCornerShape(14.dp))
                                .padding(14.dp)
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text("Operator Profile:", fontSize = 12.sp, color = BentoTextSubtitle, fontWeight = FontWeight.Medium)
                                    Text(currentUserEmail ?: "", fontSize = 13.sp, color = BentoTextDark, fontWeight = FontWeight.Bold)
                                }
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text("Organization Name:", fontSize = 12.sp, color = BentoTextSubtitle, fontWeight = FontWeight.Medium)
                                    Text(currentOrgName ?: "N/A", fontSize = 13.sp, color = BentoTextDark, fontWeight = FontWeight.Bold)
                                }
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text("Control Tier Plan:", fontSize = 12.sp, color = BentoTextSubtitle, fontWeight = FontWeight.Medium)
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(6.dp))
                                            .background(BentoPurplePrimary.copy(alpha = 0.15f))
                                            .padding(horizontal = 6.dp, vertical = 2.dp)
                                    ) {
                                        Text(currentOrgPlan ?: "BASIC", fontSize = 10.sp, color = BentoPurpleDark, fontWeight = FontWeight.Bold)
                                    }
                                }
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text("Active JWT Bearer:", fontSize = 12.sp, color = BentoTextSubtitle, fontWeight = FontWeight.Medium)
                                    Text(
                                        text = if (jwtToken != null) jwtToken!!.take(18) + "..." else "jwt_offline_token",
                                        fontSize = 11.sp,
                                        color = BentoTermGreen,
                                        fontWeight = FontWeight.Bold,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        Button(
                            onClick = {
                                viewModel.logoutUser()
                                Toast.makeText(context, "SRE Profile Signed Out", Toast.LENGTH_SHORT).show()
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color.Red.copy(alpha = 0.08f), contentColor = Color.Red),
                            border = BorderStroke(1.dp, Color.Red.copy(alpha = 0.2f)),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.fillMaxWidth().height(36.dp)
                        ) {
                            Icon(Icons.Default.Logout, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Log Out Profile Session", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    } else {
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            OutlinedTextField(
                                value = authEmailInput,
                                onValueChange = { authEmailInput = it },
                                label = { Text("E-mail address", fontSize = 11.sp) },
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.fillMaxWidth()
                            )
                            OutlinedTextField(
                                value = authPasswordInput,
                                onValueChange = { authPasswordInput = it },
                                label = { Text("Session Password", fontSize = 11.sp) },
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.fillMaxWidth()
                            )

                            if (isRegisterMode) {
                                OutlinedTextField(
                                    value = authOrgNameInput,
                                    onValueChange = { authOrgNameInput = it },
                                    label = { Text("Organization Team Name", fontSize = 11.sp) },
                                    shape = RoundedCornerShape(12.dp),
                                    modifier = Modifier.fillMaxWidth()
                                )

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
                                    listOf("BASIC", "PREMIUM", "ENTERPRISE").forEach { tier ->
                                        val isSel = authOrgPlanInput == tier
                                        OutlinedButton(
                                            onClick = { authOrgPlanInput = tier },
                                            colors = ButtonDefaults.outlinedButtonColors(
                                                containerColor = if (isSel) BentoPurplePrimary.copy(alpha = 0.1f) else Color.Transparent
                                            ),
                                            border = BorderStroke(1.dp, if (isSel) BentoPurplePrimary else BentoBorderMedium),
                                            shape = RoundedCornerShape(10.dp),
                                            modifier = Modifier.weight(1f)
                                        ) {
                                            Text(tier, fontSize = 10.sp, fontWeight = FontWeight.Bold, color = if (isSel) BentoPurplePrimary else BentoTextDark)
                                        }
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(6.dp))

                            Button(
                                onClick = {
                                    if (authEmailInput.isBlank() || authPasswordInput.isBlank()) {
                                        Toast.makeText(context, "Fill the missing form fields", Toast.LENGTH_SHORT).show()
                                        return@Button
                                    }
                                    if (isRegisterMode) {
                                        viewModel.registerUser(
                                            email = authEmailInput,
                                            password = authPasswordInput,
                                            organisation = authOrgNameInput.ifBlank { "Unassigned Corp" },
                                            plan = authOrgPlanInput,
                                            onCompleted = { msg ->
                                                Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
                                            },
                                            onError = { err ->
                                                Toast.makeText(context, err, Toast.LENGTH_SHORT).show()
                                            }
                                        )
                                    } else {
                                        viewModel.loginUser(
                                            email = authEmailInput,
                                            password = authPasswordInput,
                                            onCompleted = { msg ->
                                                Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
                                            },
                                            onError = { err ->
                                                Toast.makeText(context, err, Toast.LENGTH_SHORT).show()
                                            }
                                        )
                                    }
                                },
                                colors = ButtonDefaults.buttonColors(containerColor = BentoPurplePrimary, contentColor = Color.White),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.fillMaxWidth().height(42.dp)
                            ) {
                                Icon(Icons.Default.Send, contentDescription = null, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(if (isRegisterMode) "Create Corporate Workspace" else "Sign In SRE Admin", fontWeight = FontWeight.Bold, fontSize = 12.sp)
                            }

                            TextButton(
                                onClick = { isRegisterMode = !isRegisterMode },
                                modifier = Modifier.align(Alignment.CenterHorizontally)
                            ) {
                                Text(
                                    text = if (isRegisterMode) "Already have a profile? Sign In instead" else "New team? Create a secure organization profile",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = BentoPurplePrimary
                                )
                            }
                        }
                    }
                }
            }
        }

        // BENTO BOX CARD: Connection Status Overview
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .height(95.dp),
                    colors = CardDefaults.cardColors(containerColor = BentoContainerActive),
                    border = BorderStroke(1.dp, BentoBorderLight),
                    shape = RoundedCornerShape(20.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(14.dp),
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            "Secure Vault",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = BentoPurpleDark,
                            fontFamily = FontFamily.Monospace
                        )
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Lock, contentDescription = null, tint = BentoPurpleDark, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                "AES-256 HSM Storage",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoPurpleDark
                            )
                        }
                    }
                }

                Card(
                    modifier = Modifier
                        .weight(0.9f)
                        .height(95.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = BorderStroke(1.dp, BentoBorderMedium),
                    shape = RoundedCornerShape(20.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(14.dp),
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            "Total Connected",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = BentoTextSubtitle,
                            fontFamily = FontFamily.Monospace
                        )
                        Text(
                            text = "${accounts.size} Clouds",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = BentoTextDark
                        )
                    }
                }
            }
        }

        // BENTO BOX CARD: Live Backend API Configuration
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("fastapi_config_card"),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                border = BorderStroke(1.dp, BentoBorderMedium),
                shape = RoundedCornerShape(24.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "LIVE API ENGINE CONFIGURATION",
                        color = BentoTextSubtitle,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    var newBackendUrl by remember { mutableStateOf(com.example.api.CloudOpsBackendClient.baseUrl) }
                    
                    OutlinedTextField(
                        value = newBackendUrl,
                        onValueChange = { newBackendUrl = it },
                        label = { Text("EC2 Machine IP / Backend URL", fontSize = 12.sp) },
                        placeholder = { Text("e.g., http://<your-ec2-ip>:8000", fontSize = 13.sp) },
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    )
                    
                    Spacer(modifier = Modifier.height(10.dp))
                    
                    Button(
                        onClick = {
                            viewModel.updateBackendUrl(newBackendUrl)
                            Toast.makeText(context, "Backend URL updated to $newBackendUrl", Toast.LENGTH_SHORT).show()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = BentoPurplePrimary, contentColor = Color.White),
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth().height(42.dp)
                    ) {
                        Text("Apply EC2 Backend Configuration", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        // BENTO FORM: Add Cloud Account Form with Explicit STS Connections
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("connector_form_card"),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                border = BorderStroke(1.dp, BentoBorderMedium),
                shape = RoundedCornerShape(24.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Connect Cloud Credentials",
                        fontWeight = FontWeight.ExtraBold,
                        color = BentoTextDark,
                        fontSize = 16.sp
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    // Tab Select
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(BentoContainerMuted)
                            .padding(4.dp),
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        val providers = listOf("AWS", "Azure", "GCP")
                        providers.forEach { p ->
                            Button(
                                onClick = { activeTabAddAccount = p },
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (activeTabAddAccount == p) BentoPurplePrimary else Color.Transparent,
                                    contentColor = if (activeTabAddAccount == p) Color.White else BentoTextDark
                                ),
                                contentPadding = PaddingValues(0.dp),
                                modifier = Modifier
                                    .weight(1f)
                                    .height(34.dp)
                                    .testTag("btn_select_provider_$p")
                            ) {
                                Text(p, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Common inputs
                    OutlinedTextField(
                        value = accountNameInput,
                        onValueChange = { accountNameInput = it },
                        label = { Text("Account Nickname", fontSize = 12.sp) },
                        placeholder = { Text("e.g. Production Corporate Core", fontSize = 13.sp) },
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = BentoPurplePrimary,
                            unfocusedBorderColor = BentoBorderMedium
                        ),
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("input_account_nickname"),
                        maxLines = 1
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    OutlinedTextField(
                        value = regionInput,
                        onValueChange = { regionInput = it },
                        label = { Text("Default Resource Region/Location", fontSize = 12.sp) },
                        placeholder = { Text("e.g. us-east-1, eastus, us-central1", fontSize = 13.sp) },
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = BentoPurplePrimary,
                            unfocusedBorderColor = BentoBorderMedium
                        ),
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("input_credentials_region"),
                        maxLines = 1
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    // Provider specific credentials fields
                    AnimatedContent(
                        targetState = activeTabAddAccount,
                        label = "formTransition"
                    ) { provider ->
                        when (provider) {
                            "AWS" -> {
                                OutlinedTextField(
                                    value = awsIamArn,
                                    onValueChange = { awsIamArn = it },
                                    label = { Text("STS AssumeRole IAM ARN", fontSize = 12.sp) },
                                    placeholder = { Text("arn:aws:iam::119027251070:role/CloudOpsDiscovery", fontSize = 13.sp) },
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedBorderColor = BentoPurplePrimary,
                                        unfocusedBorderColor = BentoBorderMedium
                                    ),
                                    shape = RoundedCornerShape(12.dp),
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .testTag("input_aws_iam_arn")
                                )
                            }
                            "Azure" -> {
                                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                                    OutlinedTextField(
                                        value = azureTenantId,
                                        onValueChange = { azureTenantId = it },
                                        label = { Text("Active Directory Tenant ID", fontSize = 12.sp) },
                                        placeholder = { Text("9fcd-1234-58bc-fa39", fontSize = 13.sp) },
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = BentoPurplePrimary,
                                            unfocusedBorderColor = BentoBorderMedium
                                        ),
                                        shape = RoundedCornerShape(12.dp),
                                        modifier = Modifier.fillMaxWidth()
                                    )
                                    OutlinedTextField(
                                        value = azureClientId,
                                        onValueChange = { azureClientId = it },
                                        label = { Text("Application Client ID", fontSize = 12.sp) },
                                        placeholder = { Text("a543-de56-88ab-bc72", fontSize = 13.sp) },
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = BentoPurplePrimary,
                                            unfocusedBorderColor = BentoBorderMedium
                                        ),
                                        shape = RoundedCornerShape(12.dp),
                                        modifier = Modifier.fillMaxWidth()
                                    )
                                    OutlinedTextField(
                                        value = azureClientSecret,
                                        onValueChange = { azureClientSecret = it },
                                        label = { Text("Client Secret Key", fontSize = 12.sp) },
                                        placeholder = { Text("p@sswordSecretKey2026", fontSize = 13.sp) },
                                        colors = OutlinedTextFieldDefaults.colors(
                                            focusedBorderColor = BentoPurplePrimary,
                                            unfocusedBorderColor = BentoBorderMedium
                                        ),
                                        shape = RoundedCornerShape(12.dp),
                                        modifier = Modifier.fillMaxWidth()
                                    )
                                }
                            }
                            "GCP" -> {
                                OutlinedTextField(
                                    value = gcpServiceAccountJson,
                                    onValueChange = { gcpServiceAccountJson = it },
                                    label = { Text("Service Account JSON Keystore", fontSize = 12.sp) },
                                    placeholder = { Text("{\n  \"type\": \"service_account\",\n  \"project_id\": \"cloudops-gcp-994\"\n...", fontSize = 12.sp) },
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedBorderColor = BentoPurplePrimary,
                                        unfocusedBorderColor = BentoBorderMedium
                                    ),
                                    shape = RoundedCornerShape(12.dp),
                                    maxLines = 5,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(100.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Connect button triggering dynamic IAM role linkages
                    Button(
                        onClick = {
                            if (accountNameInput.isBlank()) {
                                Toast.makeText(context, "Please configure nickname", Toast.LENGTH_SHORT).show()
                                return@Button
                            }

                            val successCallback: (String) -> Unit = { msg ->
                                Toast.makeText(context, msg, Toast.LENGTH_LONG).show()
                                accountNameInput = ""
                                awsIamArn = ""
                                azureTenantId = ""
                                azureClientId = ""
                                azureClientSecret = ""
                                gcpServiceAccountJson = ""
                            }

                            val errorCallback: (String) -> Unit = { err ->
                                Toast.makeText(context, "Link failed: $err", Toast.LENGTH_LONG).show()
                            }

                            when (activeTabAddAccount) {
                                "AWS" -> {
                                    val targetArn = awsIamArn.ifBlank { "arn:aws:iam::119027251070:role/CloudMigrateRole" }
                                    viewModel.connectAwsCloud(
                                        roleArn = targetArn,
                                        region = regionInput,
                                        accountName = accountNameInput,
                                        onSuccess = successCallback,
                                        onError = errorCallback
                                    )
                                }
                                "Azure" -> {
                                    val tenant = azureTenantId.ifBlank { "9fcd-1234-azure-tenant" }
                                    val client = azureClientId.ifBlank { "client-id-sp-90" }
                                    val secret = azureClientSecret.ifBlank { "secret-key-33" }
                                    viewModel.connectAzureCloud(
                                        tenantId = tenant,
                                        clientId = client,
                                        clientSecret = secret,
                                        region = regionInput,
                                        accountName = accountNameInput,
                                        onSuccess = successCallback,
                                        onError = errorCallback
                                    )
                                }
                                "GCP" -> {
                                    val finalJson = gcpServiceAccountJson.ifBlank { "{\"project_id\": \"default-gcp-project\"}" }
                                    viewModel.connectGcpCloud(
                                        serviceAccountJson = finalJson,
                                        region = regionInput,
                                        accountName = accountNameInput,
                                        onSuccess = successCallback,
                                        onError = errorCallback
                                    )
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = BentoPurplePrimary, contentColor = Color.White),
                        shape = RoundedCornerShape(14.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(44.dp)
                            .testTag("submit_connect_account_button")
                    ) {
                        Icon(Icons.Default.Link, contentDescription = null)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Verify & Bind Cloud Account", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        // Vault Credentials Mapped List Header
        item {
            Text(
                text = "Configured Tenant Bonds (${accounts.size}) - Click Row to Inspect Dynamic STS Session Keys",
                fontWeight = FontWeight.ExtraBold,
                color = BentoTextDark,
                fontSize = 14.sp,
                modifier = Modifier.padding(top = 8.dp)
            )
        }

        // Configured Accounts list
        if (accounts.isEmpty()) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("No connected tenants. Use form above to secure accounts.", color = BentoTextSubtitle, fontSize = 13.sp)
                }
            }
        } else {
            items(accounts) { account ->
                ConnectedAccountRow(
                    account = account,
                    onDelete = {
                        viewModel.removeCloudAccount(account.id)
                        Toast.makeText(context, "Link to ${account.name} revoked.", Toast.LENGTH_SHORT).show()
                    },
                    onInspect = {
                        viewModel.fetchTemporalCredentialsDetails(account.id)
                        showCredentialsDialogAccount = account
                    }
                )
            }
        }
    }

    // Dynamic Rotating Credentials Dialog
    if (showCredentialsDialogAccount != null) {
        val account = showCredentialsDialogAccount!!
        AlertDialog(
            onDismissRequest = { showCredentialsDialogAccount = null },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.fetchTemporalCredentialsDetails(account.id) {
                            Toast.makeText(context, "Credentials session keys rotated successfully!", Toast.LENGTH_SHORT).show()
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = BentoPurplePrimary)
                ) {
                    Icon(Icons.Default.Autorenew, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("Rotate Keys Now", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showCredentialsDialogAccount = null }) {
                    Text("Close")
                }
            },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.VpnKey,
                        contentDescription = null,
                        tint = BentoPurplePrimary,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Dynamic STS Session Vault",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = BentoTextDark
                    )
                }
            },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                    modifier = Modifier.verticalScroll(rememberScrollState())
                ) {
                    Text(
                        text = "Real-time temporary keys assumed from parent IAM federated policy. Autorefresh triggers automatically upon expiry.",
                        fontSize = 12.sp,
                        color = BentoTextSubtitle
                    )

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(BentoContainerMuted)
                            .padding(10.dp)
                    ) {
                        Column {
                            Text(
                                text = "TENANT: ${account.name} [${account.provider}]",
                                fontWeight = FontWeight.Bold,
                                fontSize = 11.sp,
                                color = BentoPurpleDark,
                                fontFamily = FontFamily.Monospace
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "Arn hint: ${account.credentialsHint}",
                                fontSize = 10.sp,
                                color = BentoTextDark,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }

                    if (lastTemporaryCredentials != null) {
                        val tc = lastTemporaryCredentials!!
                        Text("Active Secret Lease Tokens:", fontWeight = FontWeight.Bold, fontSize = 12.sp, color = BentoTextDark)
                        
                        tc.credentials.forEach { (key, value) ->
                            Column {
                                Text(key.uppercase(), fontSize = 9.sp, fontWeight = FontWeight.Bold, color = BentoTextSubtitle)
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(BentoPromoBg)
                                        .padding(6.dp)
                                ) {
                                    Text(
                                        text = value,
                                        fontSize = 10.sp,
                                        fontFamily = FontFamily.Monospace,
                                        color = BentoAccentRed,
                                        maxLines = 2
                                    )
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Granted Permissions list:", fontWeight = FontWeight.Bold, fontSize = 12.sp, color = BentoTextDark)
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(Color(0xFFF9F7FC))
                                .border(1.dp, BentoBorderLight, RoundedCornerShape(10.dp))
                                .padding(8.dp)
                        ) {
                            Text(
                                text = tc.permissions.joinToString(", "),
                                fontSize = 10.sp,
                                fontFamily = FontFamily.Monospace,
                                color = BentoPurpleDark,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    } else {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(120.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(color = BentoPurplePrimary)
                        }
                    }
                }
            },
            shape = RoundedCornerShape(24.dp),
            containerColor = Color.White
        )
    }
}

@Composable
fun ConnectedAccountRow(
    account: CloudAccount,
    onDelete: () -> Unit,
    onInspect: () -> Unit
) {
    val cloudBgColor = when (account.provider) {
        "AWS" -> AWSLightBg
        "Azure" -> AzureLightBg
        else -> GCPLightBg
    }

    val iconVector = when (account.provider) {
        "AWS" -> Icons.Default.CloudQueue
        "Azure" -> Icons.Default.VpnKey
        else -> Icons.Default.Terminal
    }

    val iconColor = when (account.provider) {
        "AWS" -> AWSColor
        "Azure" -> AzureColor
        else -> GCPColor
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onInspect() },
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = BorderStroke(1.dp, BentoBorderMedium),
        shape = RoundedCornerShape(20.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(cloudBgColor),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = iconVector,
                        contentDescription = account.provider,
                        tint = iconColor,
                        modifier = Modifier.size(22.dp)
                    )
                }

                Spacer(modifier = Modifier.width(12.dp))

                Column {
                    Text(
                        text = account.name,
                        fontWeight = FontWeight.Bold,
                        color = BentoTextDark,
                        fontSize = 14.sp
                    )
                    Text(
                        text = "Region: ${account.region} | ${account.credentialsHint}",
                        color = BentoTextSubtitle,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        modifier = Modifier.padding(top = 2.dp)
                    )
                }
            }

            IconButton(
                onClick = onDelete,
                modifier = Modifier
                    .clip(RoundedCornerShape(10.dp))
                    .background(BentoPromoBg)
            ) {
                Icon(
                    imageVector = Icons.Default.DeleteSweep,
                    contentDescription = "Delete Account Bond",
                    tint = BentoAccentRed,
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}
