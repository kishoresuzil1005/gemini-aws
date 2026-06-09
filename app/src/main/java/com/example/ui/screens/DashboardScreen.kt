package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.DiscoveryResource
import com.example.ui.CloudViewModel
import com.example.ui.theme.*
import java.util.Locale

@Composable
fun DashboardScreen(
    viewModel: CloudViewModel,
    onNavigateToGraph: () -> Unit,
    modifier: Modifier = Modifier
) {
    val resources by viewModel.resources.collectAsState()
    val isDiscovering by viewModel.isDiscovering.collectAsState()
    val logs by viewModel.discoveryOutputLogs.collectAsState()
    val accounts by viewModel.accounts.collectAsState()
    val incidents by viewModel.incidents.collectAsState()

    var selectedRegion by remember { mutableStateOf("ALL") }
    val regionsList = listOf("ALL", "US-EAST-1", "US-WEST-2", "AP-SOUTH-1", "EU-CENTRAL-1")

    val filteredResources = remember(resources, selectedRegion) {
        if (selectedRegion == "ALL") {
            resources
        } else {
            resources.filter {
                it.configurationHint.contains(selectedRegion, ignoreCase = true) ||
                it.name.contains(selectedRegion, ignoreCase = true)
            }
        }
    }

    val activeIncidentsCount = incidents.count { it.status == "ACTIVE" }

    // Pulsing transition for the AI Insights red alarm dot
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseProgress by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse"
    )

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(BentoBg)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Welcoming and Header Block (Bento styled)
        item {
            Column {
                Text(
                    text = "CLOUD INTELLIGENCE",
                    color = BentoTextSubtitle,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    modifier = Modifier.testTag("dashboard_header")
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Stratis Platform",
                    color = BentoTextDark,
                    fontSize = 26.sp,
                    fontWeight = FontWeight.ExtraBold
                )
            }
        }

        // --- BENTO GRID BLOCK 1: MAIN AWS DISCOVERY SURFACE ---
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("bento_aws_discovery_card"),
                colors = CardDefaults.cardColors(containerColor = BentoContainerActive),
                border = BorderStroke(1.dp, BentoBorderLight),
                shape = RoundedCornerShape(28.dp)
            ) {
                Column(
                    modifier = Modifier.padding(20.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(100.dp))
                                .background(BentoPurpleDark)
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(
                                "ACTIVE DISCOVERY",
                                color = Color.White,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace,
                                letterSpacing = 1.sp
                            )
                        }
                        var expanded by remember { mutableStateOf(false) }
                        Box {
                            Row(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(BentoPurpleDark.copy(alpha = 0.15f))
                                    .clickable { expanded = true }
                                    .padding(horizontal = 8.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = selectedRegion,
                                    color = BentoPurpleDark,
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Icon(
                                    imageVector = Icons.Default.ArrowDropDown,
                                    contentDescription = "Select Region",
                                    tint = BentoPurpleDark,
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                            DropdownMenu(
                                expanded = expanded,
                                onDismissRequest = { expanded = false },
                                modifier = Modifier.background(Color.White)
                            ) {
                                regionsList.forEach { regionItem ->
                                    DropdownMenuItem(
                                        text = { 
                                            Text(
                                                text = regionItem, 
                                                fontFamily = FontFamily.Monospace,
                                                fontSize = 13.sp,
                                                fontWeight = if (selectedRegion == regionItem) FontWeight.Bold else FontWeight.Normal,
                                                color = if (selectedRegion == regionItem) BentoPurplePrimary else BentoTextDark
                                            )
                                        },
                                        onClick = {
                                            selectedRegion = regionItem
                                            expanded = false
                                        }
                                    )
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = "Environment",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = BentoPurpleDark
                    )
                    Text(
                        text = if (isDiscovering) "Syncing services in real-time..." else "Sync status: secured, indexing completed.",
                        fontSize = 13.sp,
                        color = BentoTextSubtitle,
                        lineHeight = 17.sp,
                        modifier = Modifier.padding(top = 2.dp)
                    )

                    Spacer(modifier = Modifier.height(20.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Service types
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            val serviceTypes = resources.map { it.type }.distinct().take(4)
                            serviceTypes.forEach { type ->
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(BentoPurpleDark.copy(alpha = 0.1f))
                                        .padding(horizontal = 8.dp, vertical = 4.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = type,
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = BentoPurpleDark
                                    )
                                }
                            }
                        }

                        // Nodes Count
                        Row(verticalAlignment = Alignment.Bottom) {
                            Text(
                                text = "${resources.size}",
                                fontSize = 24.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoPurpleDark
                            )
                            Spacer(modifier = Modifier.width(3.dp))
                            Text(
                                text = "running services",
                                fontSize = 12.sp,
                                color = BentoPurpleDark,
                                modifier = Modifier.padding(bottom = 3.dp)
                            )
                        }
                    }
                }
            }
        }

        // --- BENTO GRID BLOCK 2: ASYMMETRICAL COLUMN PAIR ---
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Left box: Neo4j Graph Metrics
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .height(130.dp),
                    colors = CardDefaults.cardColors(containerColor = BentoContainerMuted),
                    border = BorderStroke(1.dp, BentoBorderLight),
                    shape = RoundedCornerShape(28.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.SpaceBetween
                    ) {
                        Box(
                            modifier = Modifier
                                .size(34.dp)
                                .clip(RoundedCornerShape(10.dp))
                                .background(BentoPromoBg),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Hub,
                                contentDescription = null,
                                tint = BentoPurpleDark,
                                modifier = Modifier.size(18.dp)
                            )
                        }

                        Column {
                            Text(
                                "Neo4j Graph",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoTextDark
                            )
                            Text(
                                "${resources.size * 3} Relations",
                                fontSize = 11.sp,
                                color = BentoTextSubtitle
                            )
                        }
                    }
                }

                // Right box: AI Insights Alarm (Active pulse alert block matching mockup)
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .height(130.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = BorderStroke(1.dp, BentoBorderMedium),
                    shape = RoundedCornerShape(28.dp)
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
                                "AI INSIGHTS",
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoPurplePrimary,
                                fontFamily = FontFamily.Monospace
                            )
                            // Pulse dot indicator
                            Box(
                                modifier = Modifier
                                    .size(10.dp)
                                    .clip(RoundedCornerShape(5.dp))
                                    .background(BentoAccentRed.copy(alpha = pulseProgress))
                                    .border(1.dp, BentoAccentRed, RoundedCornerShape(5.dp))
                            )
                        }

                        Column {
                            Text(
                                text = String.format(Locale.US, "%02d", activeIncidentsCount),
                                fontSize = 32.sp,
                                fontWeight = FontWeight.Light,
                                color = BentoTextDark
                            )
                            Text(
                                text = if (activeIncidentsCount > 0) "Security Risks" else "Zero Security Risks",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Medium,
                                color = if (activeIncidentsCount > 0) BentoAccentRed else BentoTermGreen
                            )
                        }
                    }
                }
            }
        }

        // --- BENTO GRID BLOCK 3: CUSTOM LINE CHART ---
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("cost_chart_card"),
                border = BorderStroke(1.dp, BentoBorderMedium),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                shape = RoundedCornerShape(28.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "Total Monthly Cost Estimate",
                                fontWeight = FontWeight.Bold,
                                color = BentoTextDark,
                                fontSize = 16.sp
                            )
                            Text(
                                text = "Based on current real-time inventory scan",
                                color = BentoTextSubtitle,
                                fontSize = 12.sp
                            )
                        }
                        Icon(
                            imageVector = Icons.Default.AttachMoney,
                            contentDescription = "Cost",
                            tint = BentoPurplePrimary
                        )
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Text(
                        text = "$${String.format(Locale.US, "%,.2f", resources.sumOf { it.costEstimate })}",
                        fontSize = 36.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = BentoPurplePrimary
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = "Aggregated asset cost across all active cloud regions.",
                        color = BentoTextSubtitle,
                        fontSize = 12.sp
                    )
                }
            }
        }

        // --- BENTO GRID BLOCK 4: TOPOLOGY DISCOVERY SCANNER PROCESSOR PANEL ---
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("discovery_card"),
                border = BorderStroke(1.dp, BentoBorderMedium),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                shape = RoundedCornerShape(28.dp)
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Text(
                        text = "Topology Discovery Engine",
                        fontWeight = FontWeight.Bold,
                        color = BentoTextDark,
                        fontSize = 16.sp
                    )
                    Text(
                        text = "Initiate multi-cloud topology credentials sweeps to map subnets.",
                        color = BentoTextSubtitle,
                        fontSize = 12.sp
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    if (isDiscovering) {
                        Button(
                            onClick = {},
                            enabled = false,
                            colors = ButtonDefaults.buttonColors(
                                disabledContainerColor = BentoPurplePrimary.copy(alpha = 0.3f),
                                disabledContentColor = Color.White
                            ),
                            shape = RoundedCornerShape(14.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            CircularProgressIndicator(
                                color = Color.White,
                                strokeWidth = 2.dp,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Text("Discovery scan active...")
                        }
                    } else {
                        Button(
                            onClick = { viewModel.startCloudDiscovery() },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = BentoPurplePrimary,
                                contentColor = Color.White
                            ),
                            shape = RoundedCornerShape(14.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(44.dp)
                                .testTag("run_discovery_button")
                        ) {
                            Icon(Icons.Default.Terminal, contentDescription = "Terminal Run")
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                "Initiate Multi-Cloud Discovery",
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    // Terminal-style output container
                    AnimatedVisibility(
                        visible = logs.isNotEmpty(),
                        enter = expandVertically() + fadeIn(),
                        exit = shrinkVertically() + fadeOut()
                    ) {
                        Column {
                            Spacer(modifier = Modifier.height(16.dp))
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(180.dp)
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(Color(0xFF151419))
                                    .border(1.dp, BentoBorderMedium, RoundedCornerShape(12.dp))
                                    .padding(12.dp)
                            ) {
                                val scrollState = rememberScrollState()
                                LaunchedEffect(logs.size) {
                                    scrollState.animateScrollTo(scrollState.maxValue)
                                }

                                Column(
                                    modifier = Modifier
                                        .verticalScroll(scrollState)
                                        .fillMaxWidth()
                                ) {
                                    logs.forEach { log ->
                                        Text(
                                            text = log,
                                            color = if (log.contains("WARNING") || log.contains("Critical")) Color(0xFFFF9900) else if (log.contains("🤖 [Self-Heal]")) BentoPurplePrimary else Color(0xFF81C784),
                                            fontFamily = FontFamily.Monospace,
                                            fontSize = 11.sp,
                                            lineHeight = 15.sp
                                        )
                                        Spacer(modifier = Modifier.height(4.dp))
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // --- SPEC SECTION HEADER: DISCOVERED RESOURCES ----
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = if (selectedRegion == "ALL") "Discovered Catalog (${filteredResources.size})" else "Catalog: $selectedRegion (${filteredResources.size})",
                    fontWeight = FontWeight.ExtraBold,
                    color = BentoTextDark,
                    fontSize = 18.sp
                )
                TextButton(onClick = onNavigateToGraph) {
                    Text("Interactive Graph", color = BentoPurplePrimary, fontWeight = FontWeight.Bold)
                    Icon(
                        Icons.Default.ArrowForward,
                        contentDescription = "Forward arrow",
                        modifier = Modifier.size(16.dp),
                        tint = BentoPurplePrimary
                    )
                }
            }
        }

        items(filteredResources.take(8)) { resource ->
            ResourceItemRow(resource = resource)
        }
    }
}


@Composable
fun ResourceItemRow(resource: DiscoveryResource) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        border = BorderStroke(1.dp, BentoBorderMedium),
        colors = CardDefaults.cardColors(containerColor = Color.White),
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
                        .size(42.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(BentoContainerMuted),
                    contentAlignment = Alignment.Center
                ) {
                    val icon = when (resource.type) {
                        "VPC" -> Icons.Default.NetworkPing
                        "ALB" -> Icons.Default.AltRoute
                        "EC2" -> Icons.Default.Memory
                        "RDS" -> Icons.Default.Storage
                        "S3" -> Icons.Default.FolderOpen
                        "Lambda" -> Icons.Default.OfflineBolt
                        "SQS" -> Icons.Default.Queue
                        "SNS" -> Icons.Default.CellTower
                        else -> Icons.Default.CloudQueue
                    }
                    val iconColor = when (resource.type) {
                        "EC2" -> AWSColor
                        "RDS" -> AzureColor
                        "S3" -> BentoAccentRed
                        "Lambda" -> BentoPurplePrimary
                        else -> BentoPurpleDark
                    }
                    Icon(
                        imageVector = icon,
                        contentDescription = resource.type,
                        tint = iconColor,
                        modifier = Modifier.size(20.dp)
                    )
                }
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = resource.name,
                        color = BentoTextDark,
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                    Text(
                        text = "${resource.type} • ${resource.configurationHint.take(34)}...",
                        color = BentoTextSubtitle,
                        fontSize = 11.sp
                    )
                }
            }
            Text(
                text = if (resource.costEstimate > 0) "$${String.format(Locale.US, "%,.1f", resource.costEstimate)}/mo" else "Free",
                color = if (resource.costEstimate > 200) BentoAccentRed else BentoTextDark,
                fontWeight = FontWeight.Bold,
                fontSize = 13.sp
            )
        }
    }
}
