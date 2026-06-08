package com.example.ui.screens

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
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.CloudViewModel
import com.example.ui.CloudIncident
import com.example.ui.BackgroundJob
import com.example.ui.SelfHealAction
import com.example.ui.theme.*
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AiDoctorScreen(
    viewModel: CloudViewModel,
    modifier: Modifier = Modifier
) {
    val incidents by viewModel.incidents.collectAsState()
    val activeJobs by viewModel.activeJobs.collectAsState()
    val isGeneratingAi by viewModel.isGeneratingAi.collectAsState()
    val chatMessages by viewModel.chatMessages.collectAsState()

    var selectedIncidentForDiagnosis by remember { mutableStateOf<CloudIncident?>(null) }
    var showingDiagnosisDialog by remember { mutableStateOf(false) }

    // When the model finishes generating a report, let's show the most recent bot message
    LaunchedEffect(isGeneratingAi) {
        if (!isGeneratingAi && selectedIncidentForDiagnosis != null) {
            val lastMsg = chatMessages.lastOrNull()
            if (lastMsg != null && !lastMsg.isUser) {
                showingDiagnosisDialog = true
            }
        }
    }

    val activeCount = incidents.count { it.status == "ACTIVE" }
    val healingCount = incidents.count { it.status == "HEALING" }
    val resolvedCount = incidents.count { it.status == "RESOLVED" }
    val safetyScore = when {
        activeCount == 0 -> 98
        activeCount == 1 -> 85
        activeCount == 2 -> 68
        else -> 45
    }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(BentoBg)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Upper Title Block
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "AUTONOMIC HEALING CONTROL PANEL",
                        color = BentoTextSubtitle,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "AI Operations Doctor",
                        color = BentoTextDark,
                        fontSize = 26.sp,
                        fontWeight = FontWeight.ExtraBold
                    )
                }

                // Reset Action trigger Button
                IconButton(
                    onClick = { viewModel.resetIncidents() },
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(BentoContainerMuted)
                ) {
                    Icon(
                        imageVector = Icons.Default.Refresh,
                        contentDescription = "Reset Alerts",
                        tint = BentoPurplePrimary,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }

        // STATS MATRIX BENTO BOXES ROW
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Posture Score Bento Box
                Card(
                    modifier = Modifier
                        .weight(1.2f)
                        .height(115.dp),
                    colors = CardDefaults.cardColors(containerColor = BentoContainerActive),
                    border = BorderStroke(1.dp, BentoBorderLight),
                    shape = RoundedCornerShape(24.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "Safety Posture",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoPurpleDark,
                                fontFamily = FontFamily.Monospace
                            )
                            Box(
                                modifier = Modifier
                                    .size(6.dp)
                                    .clip(RoundedCornerShape(3.dp))
                                    .background(if (activeCount == 0) BentoTermGreen else BentoAccentRed)
                            )
                        }
                        Row(
                            verticalAlignment = Alignment.Bottom
                        ) {
                            Text(
                                text = "$safetyScore%",
                                fontSize = 36.sp,
                                fontWeight = FontWeight.ExtraBold,
                                color = BentoPurpleDark
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "stable",
                                fontSize = 12.sp,
                                color = BentoTextSubtitle,
                                modifier = Modifier.padding(bottom = 6.dp)
                            )
                        }
                    }
                }

                // AI Active Outages Bento Box
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .height(115.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = BorderStroke(1.dp, BentoBorderMedium),
                    shape = RoundedCornerShape(24.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            "Active Alerts",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = BentoTextSubtitle,
                            fontFamily = FontFamily.Monospace
                        )
                        Column {
                            Text(
                                text = String.format(Locale.US, "%02d", activeCount),
                                fontSize = 32.sp,
                                fontWeight = FontWeight.Light,
                                color = if (activeCount > 0) BentoAccentRed else BentoTextDark
                            )
                            Text(
                                text = if (activeCount > 0) "Immediate fixes" else "All healed up",
                                fontSize = 11.sp,
                                color = BentoTextSubtitle
                            )
                        }
                    }
                }
            }
        }

        // SECOND ROW MATRIX CARD (Healed vs Progress)
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Healed Block
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .height(84.dp),
                    colors = CardDefaults.cardColors(containerColor = BentoContainerMuted),
                    border = BorderStroke(1.dp, BentoBorderLight),
                    shape = RoundedCornerShape(20.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                "Auto-Healed",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoTextSubtitle,
                                fontFamily = FontFamily.Monospace
                            )
                            Text(
                                "$resolvedCount Incidents",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoTextDark
                            )
                        }
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .background(BentoTermGreen.copy(alpha = 0.15f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Default.Verified, contentDescription = null, tint = BentoTermGreen, modifier = Modifier.size(18.dp))
                        }
                    }
                }

                // Daemon Active tasks card
                Card(
                    modifier = Modifier
                        .weight(1.1f)
                        .height(84.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = BorderStroke(1.dp, BentoBorderMedium),
                    shape = RoundedCornerShape(20.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                "Worker Daemon",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoTextSubtitle,
                                fontFamily = FontFamily.Monospace
                            )
                            Text(
                                text = if (healingCount > 0) "Heal Executing" else "Sensing logs",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = if (healingCount > 0) BentoPurplePrimary else BentoTermGreen
                            )
                        }
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .background((if (healingCount > 0) BentoPurplePrimary else BentoBorderLight).copy(alpha = 0.15f)),
                            contentAlignment = Alignment.Center
                        ) {
                            if (healingCount > 0) {
                                CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp, color = BentoPurplePrimary)
                            } else {
                                Icon(Icons.Default.HourglassEmpty, contentDescription = null, tint = BentoTextSubtitle, modifier = Modifier.size(18.dp))
                            }
                        }
                    }
                }
            }
        }

        // Section Title: Incident Action Alerts
        item {
            Text(
                text = "Operational Inquiries & Active Risks",
                fontWeight = FontWeight.ExtraBold,
                color = BentoTextDark,
                fontSize = 18.sp,
                modifier = Modifier.padding(top = 8.dp)
            )
        }

        // Live Incident List Cards
        if (incidents.isEmpty()) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("No incidents recorded in cloud telemetries.", color = BentoTextSubtitle, fontSize = 14.sp)
                }
            }
        } else {
            items(incidents) { incident ->
                IncidentControlCard(
                    incident = incident,
                    activeJobs = activeJobs,
                    isDiagnosingSelf = isGeneratingAi && selectedIncidentForDiagnosis?.id == incident.id,
                    onDiagnose = {
                        selectedIncidentForDiagnosis = incident
                        viewModel.diagnoseIncident(incident)
                    },
                    onSelfHeal = {
                        viewModel.executeSelfHeal(incident.id)
                    }
                )
            }
        }
    }

    // Modal dialogue container displaying recent Gemini diagnosis report
    if (showingDiagnosisDialog && selectedIncidentForDiagnosis != null) {
        val lastBotMsg = chatMessages.lastOrNull { !it.isUser }
        AlertDialog(
            onDismissRequest = { showingDiagnosisDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = BentoPurplePrimary)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "AI Doctor Diagnostics",
                        fontWeight = FontWeight.Black,
                        color = BentoTextDark,
                        fontSize = 18.sp
                    )
                }
            },
            text = {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(max = 380.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    Text(
                        text = "Analysis of: ${selectedIncidentForDiagnosis?.title}",
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        color = BentoTextSubtitle,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    MarkdownStyledText(
                        text = lastBotMsg?.text ?: "Failed to retrieve doctor analysis log report.",
                        baseColor = BentoTextDark
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = { showingDiagnosisDialog = false },
                    colors = ButtonDefaults.buttonColors(containerColor = BentoPurplePrimary, contentColor = Color.White)
                ) {
                    Text("Close Diagnostics", fontWeight = FontWeight.Bold)
                }
            },
            containerColor = Color.White,
            tonalElevation = 16.dp,
            shape = RoundedCornerShape(24.dp)
        )
    }
}

@Composable
fun IncidentControlCard(
    incident: CloudIncident,
    activeJobs: List<BackgroundJob>,
    isDiagnosingSelf: Boolean,
    onDiagnose: () -> Unit,
    onSelfHeal: () -> Unit
) {
    val severityColor = when (incident.severity) {
        "CRITICAL" -> BentoAccentRed
        "WARNING" -> Color(0xFFFF9900)
        else -> BentoTermGreen
    }

    val matchingJob = activeJobs.find { it.name.contains(incident.title.take(10)) || it.id.startsWith("heal") }
    val progress = matchingJob?.progress ?: 0f
    val progressPercent = (progress * 100).toInt()

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .testTag("incident_card_${incident.id}"),
        colors = CardDefaults.cardColors(
            containerColor = when (incident.status) {
                "RESOLVED" -> Color(0xFFE8F5E9) // Subtle, healthy green
                "HEALING" -> BentoPromoBg
                else -> Color.White
            }
        ),
        border = BorderStroke(
            width = 1.dp,
            color = when (incident.status) {
                "RESOLVED" -> BentoTermGreen.copy(alpha = 0.3f)
                "HEALING" -> BentoBorderLight
                else -> BentoBorderMedium
            }
        ),
        shape = RoundedCornerShape(24.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header: Title and Status Dots
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Row(
                    modifier = Modifier.weight(1f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(RoundedCornerShape(4.dp))
                            .background(severityColor)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = incident.title,
                        fontWeight = FontWeight.ExtraBold,
                        color = BentoTextDark,
                        fontSize = 15.sp
                    )
                }

                // Interactive Badge representing Status
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(100.dp))
                        .background(
                            when (incident.status) {
                                "RESOLVED" -> BentoTermGreen.copy(alpha = 0.15f)
                                "HEALING" -> BentoPurplePrimary.copy(alpha = 0.15f)
                                else -> BentoAccentRed.copy(alpha = 0.10f)
                            }
                        )
                        .border(
                            1.dp,
                            when (incident.status) {
                                "RESOLVED" -> BentoTermGreen
                                "HEALING" -> BentoPurplePrimary
                                else -> BentoAccentRed.copy(alpha = 0.4f)
                            },
                            RoundedCornerShape(100.dp)
                        )
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = incident.status,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace,
                        color = when (incident.status) {
                            "RESOLVED" -> BentoTermGreen
                            "HEALING" -> BentoPurplePrimary
                            else -> BentoAccentRed
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Body Description text
            Text(
                text = incident.description,
                color = BentoTextSubtitle,
                fontSize = 13.sp,
                lineHeight = 17.sp
            )

            Spacer(modifier = Modifier.height(6.dp))

            // Caption mapping targets
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.CloudQueue,
                    contentDescription = null,
                    tint = BentoTextSubtitle,
                    modifier = Modifier.size(12.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = "Resource: ${incident.resourceId}",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    color = BentoTextSubtitle
                )
            }

            // Real-time operations actions triggers drawer block
            if (incident.status == "ACTIVE") {
                Spacer(modifier = Modifier.height(14.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Diagnose
                    OutlinedButton(
                        onClick = onDiagnose,
                        enabled = !isDiagnosingSelf,
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = BentoPurplePrimary),
                        border = BorderStroke(1.dp, BentoBorderLight),
                        shape = RoundedCornerShape(14.dp),
                        modifier = Modifier
                            .weight(1f)
                            .height(40.dp)
                            .testTag("diagnose_button_${incident.id}")
                    ) {
                        if (isDiagnosingSelf) {
                            CircularProgressIndicator(modifier = Modifier.size(14.dp), strokeWidth = 2.dp, color = BentoPurplePrimary)
                        } else {
                            Icon(Icons.Default.AutoAwesome, contentDescription = null, modifier = Modifier.size(14.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Diagnose", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }

                    // Self-Heal
                    Button(
                        onClick = onSelfHeal,
                        colors = ButtonDefaults.buttonColors(containerColor = BentoPurplePrimary, contentColor = Color.White),
                        shape = RoundedCornerShape(14.dp),
                        modifier = Modifier
                            .weight(1f)
                            .height(40.dp)
                            .testTag("heal_button_${incident.id}")
                    ) {
                        Icon(Icons.Default.FlashOn, contentDescription = null, modifier = Modifier.size(14.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Self-Heal", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
            } else if (incident.status == "HEALING") {
                Spacer(modifier = Modifier.height(12.dp))
                Card(
                    colors = CardDefaults.cardColors(containerColor = Color.Black.copy(alpha = 0.04f)),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(10.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "Executing remediation tasks...",
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace,
                                color = BentoPurplePrimary,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                "$progressPercent%",
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace,
                                color = BentoPurplePrimary,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        LinearProgressIndicator(
                            progress = progress,
                            color = BentoPurplePrimary,
                            trackColor = BentoBorderLight,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(6.dp)
                                .clip(RoundedCornerShape(3.dp))
                        )
                    }
                }
            } else if (incident.status == "RESOLVED") {
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(BentoTermGreen.copy(alpha = 0.08f))
                        .padding(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.Verified,
                        contentDescription = "Success Resolved Check",
                        tint = BentoTermGreen,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Remedied Autonomically at ${incident.timestamp}",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = BentoTermGreen,
                        fontFamily = FontFamily.Monospace
                    )
                }
            }
        }
    }
}
