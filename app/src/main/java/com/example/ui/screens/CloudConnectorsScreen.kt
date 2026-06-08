package com.example.ui.screens

import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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

    var activeTabAddAccount by remember { mutableStateOf("AWS") }
    var accountNameInput by remember { mutableStateOf("") }
    var regionInput by remember { mutableStateOf("us-east-1") }

    // Forms fields
    var awsIamArn by remember { mutableStateOf("") }
    var azureTenantId by remember { mutableStateOf("") }
    var azureClientId by remember { mutableStateOf("") }
    var azureClientSecret by remember { mutableStateOf("") }
    var gcpServiceAccountJson by remember { mutableStateOf("") }

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
                                "AES-256 Room Storage",
                                fontSize = 12.sp,
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

        // BENTO BOX CARD: FastAPI Integration Switchboard
        item {
            val useBackend by viewModel.useBackend.collectAsState()
            val isBackendConnected by viewModel.isBackendConnected.collectAsState()

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("fastapi_switchboard_card"),
                colors = CardDefaults.cardColors(containerColor = if (isBackendConnected) Color(0xFFF0FDF4) else Color(0xFFFEF2F2)),
                border = BorderStroke(1.dp, if (isBackendConnected) Color(0xFFBBF7D0) else Color(0xFFFCA5A5)),
                shape = RoundedCornerShape(24.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                "INTEGRATION SWITCHBOARD",
                                color = if (isBackendConnected) Color(0xFF15803D) else Color(0xFFB91C1C),
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                "FastAPI SRE Engine",
                                fontWeight = FontWeight.ExtraBold,
                                color = BentoTextDark,
                                fontSize = 18.sp
                            )
                        }
                        
                        Switch(
                            checked = useBackend,
                            onCheckedChange = { viewModel.setUseBackend(it) },
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = Color.White,
                                checkedTrackColor = BentoPurplePrimary,
                            ),
                            modifier = Modifier.testTag("fastapi_gateway_switch")
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))
                    
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (isBackendConnected) Color(0xFFDCFCE7) else Color(0xFFFEE2E2))
                            .padding(horizontal = 12.dp, vertical = 8.dp)
                    ) {
                        Icon(
                            imageVector = if (isBackendConnected) Icons.Default.CloudDone else Icons.Default.CloudOff,
                            contentDescription = null,
                            tint = if (isBackendConnected) Color(0xFF166534) else Color(0xFF991B1B),
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(
                                text = if (isBackendConnected) "ONLINE: SRE Core Active" else "OFFLINE: Local Cache State",
                                fontWeight = FontWeight.Bold,
                                color = if (isBackendConnected) Color(0xFF166534) else Color(0xFF991B1B),
                                fontSize = 12.sp
                            )
                            Text(
                                text = if (isBackendConnected) "Scanning live AWS credentials + compiling DevOps diagnostics" else "Relying on standalone local Room Database simulation",
                                color = if (isBackendConnected) Color(0xFF15803D) else Color(0xFFB91C1C),
                                fontSize = 10.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }

                    if (useBackend) {
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Gateway Endpoint: ${com.example.api.CloudOpsBackendClient.baseUrl}",
                                color = BentoTextSubtitle,
                                fontSize = 10.sp,
                                fontFamily = FontFamily.Monospace,
                                modifier = Modifier.weight(1f)
                            )
                            
                            IconButton(
                                onClick = { viewModel.refreshAllFeeds() },
                                modifier = Modifier.size(24.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Refresh,
                                    contentDescription = "Sync",
                                    tint = BentoPurplePrimary,
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        }
                    }
                }
            }
        }

        // BENTO FORM: Add Cloud Account Form
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
                                        placeholder = { Text("p@sswordSecretKéy2026", fontSize = 13.sp) },
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

                    // Connect button
                    Button(
                        onClick = {
                            if (accountNameInput.isBlank()) {
                                Toast.makeText(context, "Please configure nickname", Toast.LENGTH_SHORT).show()
                                return@Button
                            }

                            val credentialsHintValue = when (activeTabAddAccount) {
                                "AWS" -> "Role ARN: " + awsIamArn.ifBlank { "arn:aws:iam::111222333:role/CloudOpsDiscovery" }
                                "Azure" -> "Tenant: " + azureTenantId.ifBlank { "9fcd-1234-azure-tenant" }
                                "GCP" -> "GCP Project Key: " + (if (gcpServiceAccountJson.contains("project_id")) "JSON Config Key" else "Service Account Default")
                                else -> "Default connection hint"
                            }

                            viewModel.addCloudAccount(
                                provider = activeTabAddAccount,
                                name = accountNameInput,
                                credentialsHint = credentialsHintValue,
                                region = regionInput.ifBlank { "default-region" }
                            )

                            // Clear inputs
                            accountNameInput = ""
                            awsIamArn = ""
                            azureTenantId = ""
                            azureClientId = ""
                            azureClientSecret = ""
                            gcpServiceAccountJson = ""

                            Toast.makeText(context, "Secure link to Room Successful!", Toast.LENGTH_SHORT).show()
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
                text = "Configured Tenant Bonds (${accounts.size})",
                fontWeight = FontWeight.ExtraBold,
                color = BentoTextDark,
                fontSize = 18.sp,
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
                    }
                )
            }
        }
    }
}

@Composable
fun ConnectedAccountRow(
    account: CloudAccount,
    onDelete: () -> Unit
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
        modifier = Modifier.fillMaxWidth(),
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
                // Cloud Logo placeholder
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
