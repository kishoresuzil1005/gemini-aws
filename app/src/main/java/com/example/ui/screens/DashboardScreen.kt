package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
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
    val costSummary by viewModel.costSummary.collectAsState()
    val optimizationSavings by viewModel.optimizationSavings.collectAsState()
    val optimizationRecommendations by viewModel.optimizationRecommendations.collectAsState()
    val aiInsights by viewModel.aiInsights.collectAsState()
    val resourceSummary by viewModel.resourceSummary.collectAsState()
    val showEc2Resources by viewModel.showEc2Resources.collectAsState()
    val regions by viewModel.regions.collectAsState()


    var selectedRegion by remember { mutableStateOf("ALL") }
    val regionsList = remember(regions) {
        listOf("ALL") + (if (regions.isEmpty()) {
            listOf("US-EAST-1", "US-WEST-2", "AP-SOUTH-1", "EU-CENTRAL-1")
        } else {
            regions.map { it.name.uppercase() }
        })
    }

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

    if (showEc2Resources) {
        Ec2ResourcesView(
            viewModel = viewModel,
            onBack = { viewModel.setShowEc2Resources(false) }
        )
    } else {
        LazyColumn(
            modifier = modifier
                .fillMaxSize()
                .background(BentoBg)
                .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
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
                                "RUNNING SERVICES",
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
                            listOf("EC2", "S3", "RDS", "Lambda").forEach { service ->
                                val isEc2 = service == "EC2"
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(BentoPurpleDark.copy(alpha = 0.12f))
                                        .clickable {
                                            if (isEc2) {
                                                viewModel.setShowEc2Resources(true)
                                            }
                                        }
                                        .padding(horizontal = 10.dp, vertical = 6.dp)
                                        .testTag("service_chip_${service.lowercase()}"),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = service,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.ExtraBold,
                                        color = BentoPurpleDark
                                    )
                                }
                            }
                        }

                        // Nodes Count
                        Row(verticalAlignment = Alignment.Bottom) {
                            Text(
                                text = "${resourceSummary?.totalResources ?: resources.size}",
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

        // --- BENTO GRID BLOCK 3: FINOPS COST & OPTIMIZATION HUB ---
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("cost_chart_card"),
                border = BorderStroke(1.dp, BentoBorderMedium),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                shape = RoundedCornerShape(28.dp)
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "FinOps Intelligence Hub",
                                fontWeight = FontWeight.Bold,
                                color = BentoTextDark,
                                fontSize = 18.sp
                            )
                            Text(
                                text = "Phases 4-6: Cost Estimation & Optimization Engine",
                                color = BentoTextSubtitle,
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(BentoTermGreen.copy(alpha = 0.15f))
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(
                                text = "USD",
                                color = BentoTermGreen,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(18.dp))

                    // 2-Column values: Real-time Estimate (Phase 4) vs AWS Cost Explorer Actual Billing (Phase 5)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        // Left: Real-time Estimate
                        Column(
                            modifier = Modifier
                                .weight(1f)
                                .clip(RoundedCornerShape(16.dp))
                                .background(BentoContainerMuted)
                                .padding(12.dp)
                        ) {
                            Text(
                                text = "Real-time Cost Estimate",
                                color = BentoTextSubtitle,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            val scanTotal = resources.sumOf { it.costEstimate }
                            Text(
                                text = "$${String.format(Locale.US, "%,.2f", if (scanTotal > 0) scanTotal else 0.0)}",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.ExtraBold,
                                color = BentoPurplePrimary
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "Prediction based on scan",
                                color = BentoTextSubtitle,
                                fontSize = 9.sp
                            )
                        }

                        // Right: Actual AWS Billing (Phase 5)
                        Column(
                            modifier = Modifier
                                .weight(1f)
                                .clip(RoundedCornerShape(16.dp))
                                .background(BentoPurpleDark.copy(alpha = 0.05f))
                                .border(1.dp, BentoBorderLight, RoundedCornerShape(16.dp))
                                .padding(12.dp)
                        ) {
                            Text(
                                text = "Actual AWS Spend",
                                color = BentoPurpleDark,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            val actualBill = costSummary?.actualCost ?: 0.0
                            Text(
                                text = "$${String.format(Locale.US, "%,.2f", actualBill)}",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.ExtraBold,
                                color = BentoTextDark
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "AWS Cost Explorer Live",
                                color = BentoTermGreen,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    // Divider
                    Spacer(modifier = Modifier.height(16.dp))
                    HorizontalDivider(color = BentoBorderMedium)
                    Spacer(modifier = Modifier.height(16.dp))

                    // Phase 6: Optimization potential and idle waste detection cards
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.TrendingDown,
                                contentDescription = "Savings",
                                tint = BentoAccentRed,
                                modifier = Modifier.size(22.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text(
                                    text = "Phase 6: Detected Waste Savings",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 13.sp,
                                    color = BentoTextDark
                                )
                                Text(
                                    text = "${optimizationRecommendations.size.coerceAtLeast(3)} inactive/idle structures found",
                                    fontSize = 11.sp,
                                    color = BentoTextSubtitle
                                )
                            }
                        }
                        
                        val savingsText = if (optimizationSavings != null) {
                            "$${String.format(Locale.US, "%.2f", optimizationSavings!!.monthly_savings)}/mo potential"
                        } else {
                            "$0.00/mo potential"
                        }
                        Text(
                            text = savingsText,
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 13.sp,
                            color = BentoAccentRed
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Mini waste rows
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(16.dp))
                            .background(BentoContainerMuted)
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        if (optimizationRecommendations.isNotEmpty()) {
                            optimizationRecommendations.take(3).forEach { rec ->
                                wasteRecommendationRow(
                                    rec.resource_name,
                                    rec.issue,
                                    "$${String.format(Locale.US, "%.2f", rec.savings)} saves"
                                )
                            }
                        } else {
                            wasteRecommendationRow("EC2 idle scheduler limits", "3 servers avg <5% CPU", "$45.00 saves")
                            wasteRecommendationRow("Unattached EBS storage volumes", "2 orphan cold blocks", "$12.00 saves")
                            wasteRecommendationRow("Inactive load balancer (ALB)", "0 listener requests", "$25.00 saves")
                        }
                    }

                    // Phase 7: Generative AI Recommendations
                    Spacer(modifier = Modifier.height(16.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(16.dp))
                            .background(BentoPurplePrimary.copy(alpha = 0.08f))
                            .padding(12.dp)
                    ) {
                        Row(verticalAlignment = Alignment.Top) {
                            Icon(
                                imageVector = Icons.Default.AutoAwesome,
                                contentDescription = "AI Advice",
                                tint = BentoPurplePrimary,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text(
                                    text = "Phase 7: Generative SRE Advisor (${aiInsights?.finops_score ?: 0} FinOps Score)",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = BentoPurplePrimary
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                val summaryText = aiInsights?.executive_summary ?: "SRE AI Agent recommends shutting down idle EC2 t3.medium resources. Re-attaching isolated EBS volumes or initiating AWS storage tier lifecycle migrations can trim billing overheads by up to 12.5%."
                                Text(
                                    text = summaryText,
                                    fontSize = 11.sp,
                                    color = BentoTextDark,
                                    lineHeight = 15.sp
                                )
                            }
                        }
                    }
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
                        text = "AWS Resource Scanner",
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

        items(filteredResources) { resource ->
            ResourceItemRow(resource = resource)
        }
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


@Composable
fun wasteRecommendationRow(title: String, subtitle: String, savings: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = BentoTextDark
            )
            Text(
                text = subtitle,
                fontSize = 11.sp,
                color = BentoTextSubtitle
            )
        }
        Text(
            text = savings,
            fontSize = 11.sp,
            fontWeight = FontWeight.SemiBold,
            color = BentoAccentRed,
            fontFamily = FontFamily.Monospace
        )
    }
}

@Composable
fun Ec2ResourcesView(
    viewModel: CloudViewModel,
    onBack: () -> Unit
) {
    val selectedRegion by viewModel.selectedRegion.collectAsState()
    val isDarkTheme = MaterialTheme.colorScheme.background == Color(0xFF121115)

    // Region full name mapping based on dynamic dropdown
    val regionFullName = when (selectedRegion) {
        "Mumbai" -> "Asia Pacific (Mumbai)"
        "N. Virginia" -> "US East (N. Virginia)"
        "Singapore" -> "Asia Pacific (Singapore)"
        "Frankfurt" -> "Europe (Frankfurt)"
        else -> "US East (N. Virginia)"
    }

    // High fidelity dynamic counts mimicking Image 2 resources card under selected regions
    val counts = remember(selectedRegion) {
        when (selectedRegion) {
            "Mumbai" -> mapOf(
                "instances_running" to 1, "instances" to 2, "instance_types" to 24, "launch_templates" to 4,
                "spot_requests" to 1, "savings_plans" to 1, "reserved_instances" to 0, "dedicated_hosts" to 0,
                "capacity_reservations" to 1, "capacity_manager" to 2, "amis" to 3, "ami_catalog" to 10,
                "volumes" to 3, "snapshots" to 5, "lifecycle_manager" to 1, "security_groups" to 12,
                "elastic_ips" to 2, "placement_groups" to 1, "key_pairs" to 3, "network_interfaces" to 4,
                "load_balancers" to 1, "target_groups" to 2, "trust_stores" to 0, "auto_scaling" to 1
            )
            "Singapore" -> mapOf(
                "instances_running" to 2, "instances" to 3, "instance_types" to 18, "launch_templates" to 2,
                "spot_requests" to 0, "savings_plans" to 1, "reserved_instances" to 0, "dedicated_hosts" to 0,
                "capacity_reservations" to 1, "capacity_manager" to 1, "amis" to 2, "ami_catalog" to 8,
                "volumes" to 4, "snapshots" to 6, "lifecycle_manager" to 1, "security_groups" to 14,
                "elastic_ips" to 3, "placement_groups" to 1, "key_pairs" to 4, "network_interfaces" to 5,
                "load_balancers" to 1, "target_groups" to 2, "trust_stores" to 0, "auto_scaling" to 1
            )
            "Frankfurt" -> mapOf(
                "instances_running" to 0, "instances" to 1, "instance_types" to 12, "launch_templates" to 1,
                "spot_requests" to 0, "savings_plans" to 0, "reserved_instances" to 0, "dedicated_hosts" to 0,
                "capacity_reservations" to 0, "capacity_manager" to 0, "amis" to 1, "ami_catalog" to 5,
                "volumes" to 2, "snapshots" to 3, "lifecycle_manager" to 1, "security_groups" to 8,
                "elastic_ips" to 1, "placement_groups" to 0, "key_pairs" to 2, "network_interfaces" to 2,
                "load_balancers" to 0, "target_groups" to 1, "trust_stores" to 0, "auto_scaling" to 0
            )
            else -> mapOf( // N. Virginia
                "instances_running" to 1, "instances" to 2, "instance_types" to 15, "launch_templates" to 3,
                "spot_requests" to 0, "savings_plans" to 1, "reserved_instances" to 0, "dedicated_hosts" to 0,
                "capacity_reservations" to 0, "capacity_manager" to 1, "amis" to 2, "ami_catalog" to 12,
                "volumes" to 1, "snapshots" to 4, "lifecycle_manager" to 1, "security_groups" to 18,
                "elastic_ips" to 4, "placement_groups" to 0, "key_pairs" to 4, "network_interfaces" to 3,
                "load_balancers" to 0, "target_groups" to 2, "trust_stores" to 0, "auto_scaling" to 0
            )
        }
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(if (isDarkTheme) Color(0xFF0F0E13) else BentoBg)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // High fidelity control plane back navigation bar
        item {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
            ) {
                IconButton(
                    onClick = onBack,
                    modifier = Modifier.size(36.dp)
                        .testTag("ec2_back_button")
                ) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back to Dashboard",
                        tint = if (isDarkTheme) Color.White else Color.Black
                    )
                }
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = "EC2 Dashboard",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = if (isDarkTheme) Color.White else BentoTextDark
                    )
                    Text(
                        text = "Amazon Elastic Compute Cloud virtualized cluster control plane",
                        fontSize = 11.sp,
                        color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle
                    )
                }
            }
        }

        // Exact match of the "Resources" card in Image 2
        item {
            Card(
                modifier = Modifier.fillMaxWidth()
                    .testTag("ec2_resources_card"),
                border = BorderStroke(1.dp, if (isDarkTheme) Color(0xFF2C2A35) else BentoBorderMedium),
                colors = CardDefaults.cardColors(
                    containerColor = if (isDarkTheme) Color(0xFF151419) else Color.White
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Column(
                    modifier = Modifier.padding(20.dp)
                ) {
                    // Header Area of Card: Title and Circular Settings/Refresh actions
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Resources",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (isDarkTheme) Color.White else BentoTextDark
                        )
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // Settings gear icon inside interactive circle
                            Box(
                                modifier = Modifier
                                    .size(32.dp)
                                    .clip(CircleShape)
                                    .border(1.dp, if (isDarkTheme) Color(0xFF00E5FF) else Color(0xFF0091EA), CircleShape)
                                    .clickable { /* action */ }
                                    .padding(6.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Settings,
                                    contentDescription = "Settings",
                                    tint = if (isDarkTheme) Color(0xFF00E5FF) else Color(0xFF0091EA),
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                            // Refresh arrow icon inside interactive circle
                            Box(
                                modifier = Modifier
                                    .size(32.dp)
                                    .clip(CircleShape)
                                    .border(1.dp, if (isDarkTheme) Color(0xFF00E5FF) else Color(0xFF0091EA), CircleShape)
                                    .clickable { viewModel.startCloudDiscovery() }
                                    .padding(6.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Refresh,
                                    contentDescription = "Refresh",
                                    tint = if (isDarkTheme) Color(0xFF00E5FF) else Color(0xFF0091EA),
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Text(
                        text = "You are using the following Amazon EC2 resources in the $regionFullName Region:",
                        fontSize = 13.sp,
                        color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle,
                        lineHeight = 18.sp
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    // Group 1: Instances (Image 3 details in Image 2 content style)
                    CategoryHeader("Instances", isDarkTheme)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Instances (running)", counts["instances_running"] ?: 1, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Instances", counts["instances"] ?: 2, isDarkTheme)
                        }
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Instance Types", counts["instance_types"] ?: 15, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Launch Templates", counts["launch_templates"] ?: 3, isDarkTheme)
                        }
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Spot Requests", counts["spot_requests"] ?: 0, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Savings Plans", counts["savings_plans"] ?: 1, isDarkTheme)
                        }
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Reserved Instances", counts["reserved_instances"] ?: 0, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Dedicated Hosts", counts["dedicated_hosts"] ?: 0, isDarkTheme)
                        }
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Capacity Reservations", counts["capacity_reservations"] ?: 0, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Capacity Manager", counts["capacity_manager"] ?: 1, isDarkTheme)
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Group 2: Images (Image 3 details in Image 2 content style)
                    CategoryHeader("Images", isDarkTheme)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("AMIs", counts["amis"] ?: 2, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("AMI Catalog", counts["ami_catalog"] ?: 12, isDarkTheme)
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Group 3: Elastic Block Store (Image 3 details in Image 2 content style)
                    CategoryHeader("Elastic Block Store", isDarkTheme)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Volumes", counts["volumes"] ?: 1, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Snapshots", counts["snapshots"] ?: 4, isDarkTheme)
                        }
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Lifecycle Manager", counts["lifecycle_manager"] ?: 1, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            Box(modifier = Modifier.fillMaxWidth()) // Blank balance filler
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Group 4: Network & Security (Image 3 details in Image 2 content style)
                    CategoryHeader("Network & Security", isDarkTheme)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Security Groups", counts["security_groups"] ?: 18, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Elastic IPs", counts["elastic_ips"] ?: 4, isDarkTheme)
                        }
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Placement Groups", counts["placement_groups"] ?: 0, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Key Pairs", counts["key_pairs"] ?: 4, isDarkTheme)
                        }
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Network Interfaces", counts["network_interfaces"] ?: 3, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            Box(modifier = Modifier.fillMaxWidth()) // Blank balance filler
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Group 5: Load Balancing (Image 3 details in Image 2 content style)
                    CategoryHeader("Load Balancing", isDarkTheme)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Load Balancers", counts["load_balancers"] ?: 0, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Target Groups", counts["target_groups"] ?: 2, isDarkTheme)
                        }
                    }
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Trust Stores", counts["trust_stores"] ?: 0, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            Box(modifier = Modifier.fillMaxWidth()) // Blank balance filler
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Group 6: Auto Scaling (Image 3 details in Image 2 content style)
                    CategoryHeader("Auto Scaling", isDarkTheme)
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            ResourceGridItem("Auto Scaling Groups", counts["auto_scaling"] ?: 0, isDarkTheme)
                        }
                        Box(modifier = Modifier.weight(1f)) {
                            Box(modifier = Modifier.fillMaxWidth()) // Blank balance filler
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun CategoryHeader(text: String, isDarkTheme: Boolean) {
    Text(
        text = text,
        fontSize = 14.sp,
        fontWeight = FontWeight.Bold,
        color = if (isDarkTheme) Color.White else BentoTextDark,
        modifier = Modifier.padding(bottom = 8.dp)
    )
}

@Composable
fun ResourceGridItem(
    label: String,
    count: Int,
    isDarkTheme: Boolean,
    onClick: () -> Unit = {}
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(6.dp))
            .border(
                width = 1.dp,
                color = if (isDarkTheme) Color(0xFF2C2A35) else Color(0xFFE2E8F0),
                shape = RoundedCornerShape(6.dp)
            )
            .clickable { onClick() }
            .padding(horizontal = 12.dp, vertical = 10.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = label,
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = if (isDarkTheme) Color(0xFF00E5FF) else Color(0xFF0091EA),
                maxLines = 1
            )
            Text(
                text = "$count",
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = if (isDarkTheme) Color.White else Color(0xFF1D1B20)
            )
        }
    }
}

