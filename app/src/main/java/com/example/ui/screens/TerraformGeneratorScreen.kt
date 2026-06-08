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
import androidx.compose.material.icons.outlined.ContentCopy
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.graphics.Color
import com.example.data.SavedMigration
import com.example.ui.CloudViewModel
import com.example.ui.theme.*

@Composable
fun TerraformGeneratorScreen(
    viewModel: CloudViewModel,
    modifier: Modifier = Modifier
) {
    val sourceCloud by viewModel.sourceCloud.collectAsState()
    val targetCloud by viewModel.targetCloud.collectAsState()
    val selectedServices by viewModel.selectedServices.collectAsState()
    val generatedCode by viewModel.generatedTerraform.collectAsState()
    val isCompiling by viewModel.isGeneratingTerraform.collectAsState()
    val savedMigrations by viewModel.savedMigrations.collectAsState()

    val context = LocalContext.current
    val clipboardManager = LocalClipboardManager.current
    var migrationNameInput by remember { mutableStateOf("") }
    var showingSaveDialog by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(SpaceSlate)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Upper Title
        item {
            Column {
                Text(
                    text = "TARGET SYSTEMS MIGRATION GENERATOR",
                    color = MaterialTheme.colorScheme.primary,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Terraform Compilers",
                    color = TextWhite,
                    fontSize = 26.sp,
                    fontWeight = FontWeight.ExtraBold
                )
            }
        }

        // Segmented Settings Selectors Card
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("generator_settings_card"),
                border = BorderStroke(1.dp, BorderGrey),
                colors = CardDefaults.cardColors(containerColor = DeepCard)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Migration Configurations",
                        color = TextWhite,
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    // Source Select
                    Text("SOURCE ENVIROMENT CLOUD provider", fontSize = 10.sp, color = TextDim, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        providerButton("AWS", active = sourceCloud == "AWS", modifier = Modifier.weight(1f)) {
                            viewModel.setSourceCloud("AWS")
                        }
                        providerButton("Azure", active = sourceCloud == "Azure", enabled = false, modifier = Modifier.weight(1f)) {}
                        providerButton("GCP", active = sourceCloud == "GCP", enabled = false, modifier = Modifier.weight(1f)) {}
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Target Select
                    Text("TARGET LANDING CLOUD provider", fontSize = 10.sp, color = TextDim, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        providerButton("Azure", active = targetCloud == "Azure", modifier = Modifier.weight(1f)) {
                            viewModel.setTargetCloud("Azure")
                        }
                        providerButton("GCP", active = targetCloud == "GCP", modifier = Modifier.weight(1f)) {
                            viewModel.setTargetCloud("GCP")
                        }
                        providerButton("AWS", active = targetCloud == "AWS", enabled = false, modifier = Modifier.weight(1f)) {}
                    }
                }
            }
        }

        // Module Checkboxes Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                border = BorderStroke(1.dp, BorderGrey),
                colors = CardDefaults.cardColors(containerColor = DeepCard)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Discovered Network Modules (To Convert)",
                        color = TextWhite,
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    val availableModules = listOf(
                        "Compute (EC2/VM)",
                        "Database (RDS/SQL)",
                        "Storage (S3/Blob)",
                        "Networking (VPC/VNet)",
                        "Serverless (Lambda/AppService)"
                    )

                    availableModules.forEach { module ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { viewModel.toggleServiceSelected(module) }
                                .padding(vertical = 6.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Checkbox(
                                checked = selectedServices.contains(module),
                                onCheckedChange = { viewModel.toggleServiceSelected(module) },
                                colors = CheckboxDefaults.colors(checkedColor = CyberCyan, checkmarkColor = SpaceSlate),
                                modifier = Modifier.testTag("checkbox_${module.take(6).lowercase()}")
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = module, color = TextWhite, fontSize = 14.sp)
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    if (isCompiling) {
                        Button(
                            onClick = {},
                            enabled = false,
                            colors = ButtonDefaults.buttonColors(disabledContainerColor = ElectricBlue.copy(alpha = 0.3f)),
                            shape = RoundedCornerShape(6.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            CircularProgressIndicator(modifier = Modifier.size(18.dp), color = TextWhite, strokeWidth = 2.dp)
                            Spacer(modifier = Modifier.width(12.dp))
                            Text("Compiling HCL templates...", color = TextWhite)
                        }
                    } else {
                        Button(
                            onClick = { viewModel.runTerraformGenerator() },
                            colors = ButtonDefaults.buttonColors(containerColor = CyberCyan, contentColor = SpaceSlate),
                            shape = RoundedCornerShape(6.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .testTag("trigger_compile_button")
                        ) {
                            Icon(Icons.Default.Engineering, contentDescription = "Compile icon")
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                "Generate Target Terraform Configs",
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }
        }

        // Produced Terraform Source Output Block
        if (generatedCode.isNotEmpty() || isCompiling) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    border = BorderStroke(1.dp, CyberCyan),
                    colors = CardDefaults.cardColors(containerColor = Color.Black)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .clip(RoundedCornerShape(4.dp))
                                        .background(TerminalGreen)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "main.tf (HCL Compile)",
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 14.sp,
                                    color = TerminalGreen,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                            
                            Row {
                                // Copy Button
                                IconButton(
                                    onClick = {
                                        clipboardManager.setText(AnnotatedString(generatedCode))
                                        Toast.makeText(context, "HCL Copied to Clipboard", Toast.LENGTH_SHORT).show()
                                    },
                                    modifier = Modifier.testTag("copy_code_button")
                                ) {
                                    Icon(Icons.Outlined.ContentCopy, contentDescription = "Copy code", tint = CyberCyan, modifier = Modifier.size(18.dp))
                                }

                                // Save to database button
                                IconButton(onClick = { showingSaveDialog = true }) {
                                    Icon(Icons.Default.Save, contentDescription = "Save template", tint = ElectricBlue, modifier = Modifier.size(18.dp))
                                }
                            }
                        }

                        Divider(color = BorderGrey, modifier = Modifier.padding(vertical = 8.dp))

                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(260.dp)
                                .verticalScroll(rememberScrollState())
                        ) {
                            if (isCompiling) {
                                Column(
                                    modifier = Modifier.fillMaxSize(),
                                    verticalArrangement = Arrangement.Center,
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    CircularProgressIndicator(color = CyberCyan)
                                    Spacer(modifier = Modifier.height(12.dp))
                                    Text(
                                        "Synthesizing cloud models into standard HCL patterns. Executing Celery worker task...",
                                        color = TextDim,
                                        fontSize = 11.sp,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            } else {
                                Text(
                                    text = generatedCode,
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 11.sp,
                                    color = TerminalGreen,
                                    lineHeight = 15.sp,
                                    modifier = Modifier.fillMaxWidth()
                                )
                            }
                        }
                    }
                }
            }
        }

        // HISTORIC GENERATIONS LIST FROM ROOM DB
        item {
            Text(
                text = "Saved Deployments Local Vault (${savedMigrations.size})",
                fontWeight = FontWeight.Bold,
                color = TextWhite,
                fontSize = 18.sp
            )
        }

        if (savedMigrations.isEmpty()) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 12.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "No saved layouts persistent in SQLite.",
                        color = TextDim,
                        fontSize = 13.sp
                    )
                }
            }
        } else {
            items(savedMigrations) { migration ->
                SavedMigrationRow(
                    migration = migration,
                    onCopyCode = {
                        clipboardManager.setText(AnnotatedString(migration.terraformCode))
                        Toast.makeText(context, "Code Copied of ${migration.title}", Toast.LENGTH_SHORT).show()
                    },
                    onDelete = { viewModel.deleteMigration(migration.id) }
                )
            }
        }
    }

    // Save Migration Dialog Box
    if (showingSaveDialog) {
        AlertDialog(
            onDismissRequest = { showingSaveDialog = false },
            title = { Text("Vault Secure Save", color = TextWhite, fontWeight = FontWeight.Bold) },
            text = {
                Column {
                    Text("Describe this multi-cloud template mapping configuration to save in Room database persistence:", color = TextDim, fontSize = 13.sp)
                    Spacer(modifier = Modifier.height(12.dp))
                    TextField(
                        value = migrationNameInput,
                        onValueChange = { migrationNameInput = it },
                        placeholder = { Text("e.g. FastAPI Core Live Azure Map", fontSize = 13.sp) },
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = SpaceSlate,
                            unfocusedContainerColor = SpaceSlate,
                            unfocusedIndicatorColor = CyberCyan,
                            focusedIndicatorColor = ElectricBlue
                        ),
                        textStyle = LocalTextStyle.current.copy(color = TextWhite, fontSize = 14.sp)
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        val finalTitle = migrationNameInput.ifBlank { "Migration Workspace Layout - AWS to $targetCloud" }
                        viewModel.saveGeneratedMigration(finalTitle)
                        showingSaveDialog = false
                        migrationNameInput = ""
                        Toast.makeText(context, "Saved to SQLite Database Vault", Toast.LENGTH_SHORT).show()
                    }
                ) {
                    Text("Save Workspace", color = CyberCyan)
                }
            },
            dismissButton = {
                TextButton(onClick = { showingSaveDialog = false }) {
                    Text("Cancel", color = TextDim)
                }
            },
            containerColor = DeepCard,
            tonalElevation = 12.dp
        )
    }
}

@Composable
fun providerButton(
    name: String,
    active: Boolean,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        shape = RoundedCornerShape(6.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = if (active) ElectricBlue else SpaceSlate,
            contentColor = if (active) Color.White else TextWhite,
            disabledContainerColor = SpaceSlate.copy(alpha = 0.2f),
            disabledContentColor = TextDim.copy(alpha = 0.3f)
        ),
        border = BorderStroke(1.dp, if (active) ElectricBlue else BorderGrey),
        contentPadding = PaddingValues(0.dp),
        modifier = modifier.height(38.dp)
    ) {
        Text(
            text = name,
            fontSize = 12.sp,
            fontWeight = FontWeight.ExtraBold
        )
    }
}

@Composable
fun SavedMigrationRow(
    migration: SavedMigration,
    onCopyCode: () -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, BorderGrey),
        colors = CardDefaults.cardColors(containerColor = DeepCard)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = migration.title,
                        fontWeight = FontWeight.Bold,
                        color = TextWhite,
                        fontSize = 14.sp
                    )
                    Text(
                        text = "${migration.sourceCloud} ➔ ${migration.targetCloud}  |  Modules: ${migration.servicesMigrated}",
                        color = TextDim,
                        fontSize = 11.sp
                    )
                }

                Row {
                    IconButton(onClick = onCopyCode) {
                        Icon(Icons.Outlined.ContentCopy, contentDescription = "Copy Saved", tint = CyberCyan, modifier = Modifier.size(16.dp))
                    }
                    IconButton(onClick = onDelete) {
                        Icon(Icons.Default.Delete, contentDescription = "Delete Saved", tint = WarningAmber, modifier = Modifier.size(16.dp))
                    }
                }
            }
        }
    }
}
