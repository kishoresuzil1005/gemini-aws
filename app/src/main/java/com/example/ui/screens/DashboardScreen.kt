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
import androidx.compose.ui.draw.rotate
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
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

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
    val dashboardSummary by viewModel.dashboardSummary.collectAsState()
    val dashboardState by viewModel.dashboardState.collectAsState()
    val showEc2Resources by viewModel.showEc2Resources.collectAsState()
    val regions by viewModel.regions.collectAsState()
    val isRefreshing by viewModel.isRefreshing.collectAsState()
    val lastRefresh by viewModel.lastRefresh.collectAsState()


    val selectedRegionRaw by viewModel.selectedRegion.collectAsState()
    val selectedRegion = remember(selectedRegionRaw) { selectedRegionRaw.uppercase() }
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

    val refreshRotationProgress by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "refreshRotation"
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
            if (dashboardState.isLoading) {
                item {
                    LinearProgressIndicator(
                        modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(4.dp)),
                        color = BentoPurpleDark,
                        trackColor = BentoPurpleDark.copy(alpha = 0.2f)
                    )
                }
            }
            if (dashboardState.error != null) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFFFEBEE)),
                        border = BorderStroke(1.dp, Color(0xFFEF5350)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            text = "Dashboard API Error: ${dashboardState.error}",
                            color = Color(0xFFC62828),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium,
                            modifier = Modifier.padding(12.dp)
                        )
                    }
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
                                    "RUNNING SERVICES",
                                    color = Color.White,
                                    fontSize = 9.sp,
                                    fontWeight = FontWeight.Bold,
                                    fontFamily = FontFamily.Monospace,
                                    letterSpacing = 1.sp
                                )
                            }
                            IconButton(
                                onClick = {
                                    viewModel.onRefreshClicked()
                                },
                                modifier = Modifier.size(32.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Refresh,
                                    contentDescription = "Refresh Dashboard",
                                    tint = BentoPurpleDark,
                                    modifier = Modifier
                                        .size(18.dp)
                                        .rotate(if (isRefreshing) refreshRotationProgress else 0f)
                                )
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
                        text = if (isDiscovering) {
                            "Syncing services in real-time..."
                        } else {
                            val activeSummary = dashboardState.data ?: dashboardSummary
                            if (activeSummary != null) {
                                "Live scan: ${activeSummary.running_resources} running, ${activeSummary.stopped_resources} stopped. ${activeSummary.region_count} regions indexed."
                            } else {
                                "Sync status: secured, indexing completed."
                            }
                        },
                        fontSize = 13.sp,
                        color = BentoTextSubtitle,
                        lineHeight = 17.sp,
                        modifier = Modifier.padding(top = 2.dp)
                    )
                    if (lastRefresh != "Never") {
                        Text(
                            text = "Last synced: $lastRefresh",
                            fontSize = 11.sp,
                            color = BentoTextSubtitle.copy(alpha = 0.7f),
                            fontFamily = FontFamily.Monospace,
                            modifier = Modifier.padding(top = 4.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(0.dp)
                    )

                    Spacer(modifier = Modifier.height(20.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Service types
                        Row(
                            modifier = Modifier
                                .weight(1f)
                                .horizontalScroll(rememberScrollState())
                                .padding(end = 8.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            val activeSummary = dashboardState.data ?: dashboardSummary
                            val activeServices = if (activeSummary != null && !activeSummary.service_breakdown.isEmpty()) {
                                activeSummary.service_breakdown.keys.toList()
                            } else {
                                listOf("EC2", "S3", "RDS", "Lambda")
                            }
                            activeServices.forEach { serviceName ->
                                val serviceUpper = serviceName.uppercase()
                                val isEc2 = serviceUpper == "EC2"
                                val serviceCount = when (serviceUpper) {
                                    "EC2" -> activeSummary?.ec2
                                    "S3" -> activeSummary?.s3
                                    "RDS" -> activeSummary?.rds
                                    "LAMBDA" -> activeSummary?.lambda
                                    "VPC" -> activeSummary?.vpc
                                    "IAM" -> activeSummary?.iam
                                    "EBS" -> activeSummary?.ebs
                                    else -> activeSummary?.service_breakdown?.get(serviceName) ?: activeSummary?.service_breakdown?.get(serviceUpper)
                                }
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
                                        .testTag("service_chip_${serviceName.lowercase()}"),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = if (serviceCount != null) "$serviceUpper ($serviceCount)" else serviceUpper,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.ExtraBold,
                                        color = BentoPurpleDark
                                    )
                                }
                            }
                        }

                        // Nodes Count
                        Row(
                            verticalAlignment = Alignment.Bottom,
                            modifier = Modifier.wrapContentWidth()
                        ) {
                            val activeSummary = dashboardState.data ?: dashboardSummary
                            val displayTotal = activeSummary?.total_resources ?: filteredResources.size
                            Text(
                                text = "$displayTotal",
                                fontSize = 24.sp,
                                fontWeight = FontWeight.Bold,
                                color = BentoPurpleDark
                            )
                            Spacer(modifier = Modifier.width(3.dp))
                            Text(
                                text = "total resources",
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
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            IconButton(
                                onClick = {
                                    viewModel.refreshCostSummary(forceRefresh = true)
                                },
                                modifier = Modifier.size(28.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Refresh,
                                    contentDescription = "Refresh FinOps Cost",
                                    tint = BentoPurpleDark,
                                    modifier = Modifier.size(16.dp)
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
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "Actual AWS Spend",
                                    color = BentoPurpleDark,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                IconButton(
                                    onClick = {
                                        viewModel.refreshCostSummary(forceRefresh = true)
                                    },
                                    modifier = Modifier.size(20.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Refresh,
                                        contentDescription = "Refresh Actual Spend",
                                        tint = BentoPurpleDark,
                                        modifier = Modifier.size(12.dp)
                                    )
                                }
                            }
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
    val ec2SummaryState by viewModel.ec2Summary.collectAsState()
    val ec2ExtendedState by viewModel.ec2Extended.collectAsState()
    val dashboardSummary by viewModel.dashboardSummary.collectAsState()

    LaunchedEffect(selectedRegion) {
        viewModel.loadEC2Summary()
        viewModel.loadEC2Extended()
        viewModel.loadEC2Instances()
    }

    var viewMode by remember { mutableStateOf("grid") } // "grid" or "aws_console"
    var activeConsoleTab by remember { mutableStateOf("Instances") } // e.g. "Instances", "Instance Types"
    var selectedInstanceId by remember { mutableStateOf<String?>(null) }
    var selectedTabInDetails by remember { mutableStateOf("Details") }
    val scrollState = rememberScrollState()
    val coroutineScope = rememberCoroutineScope()
    var searchInput by remember { mutableStateOf("") }
    var isStateDropdownExpanded by remember { mutableStateOf(false) }

    // Region full name mapping based on dynamic dropdown
    val regionFullName = when (selectedRegion) {
        "Mumbai" -> "Asia Pacific (Mumbai)"
        "N. Virginia" -> "US East (N. Virginia)"
        "Singapore" -> "Asia Pacific (Singapore)"
        "Frankfurt" -> "Europe (Frankfurt)"
        else -> "US East (N. Virginia)"
    }

    val regionCode = when (selectedRegion) {
        "Mumbai" -> "ap-south-1"
        "N. Virginia" -> "us-east-1"
        "Singapore" -> "ap-southeast-1"
        "Frankfurt" -> "eu-central-1"
        else -> "us-east-1"
    }

    // High fidelity dynamic counts mimicking Image 2 resources card under selected regions
    val counts = remember(selectedRegion, ec2SummaryState, ec2ExtendedState, dashboardSummary) {
        val baseMap = when (selectedRegion) {
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

        val updatedMap = baseMap.toMutableMap()
        if (dashboardSummary != null) {
            updatedMap["instances_running"] = dashboardSummary!!.running_resources
            updatedMap["instances"] = dashboardSummary!!.ec2
            updatedMap["volumes"] = dashboardSummary!!.ebs
            updatedMap["security_groups"] = dashboardSummary!!.vpc
            updatedMap["elastic_ips"] = dashboardSummary!!.iam
        } else if (ec2SummaryState != null) {
            updatedMap["instances_running"] = ec2SummaryState!!.running_instances
            updatedMap["instances"] = ec2SummaryState!!.total_instances
            updatedMap["instance_types"] = ec2SummaryState!!.instance_types
            updatedMap["security_groups"] = ec2SummaryState!!.security_groups
            updatedMap["elastic_ips"] = ec2SummaryState!!.elastic_ips
            updatedMap["volumes"] = ec2SummaryState!!.volumes
            updatedMap["snapshots"] = ec2SummaryState!!.snapshots
        }
        if (ec2ExtendedState != null) {
            updatedMap["launch_templates"] = ec2ExtendedState!!.launch_templates
            updatedMap["spot_requests"] = ec2ExtendedState!!.spot_requests
            updatedMap["savings_plans"] = ec2ExtendedState!!.savings_plans
            updatedMap["reserved_instances"] = ec2ExtendedState!!.reserved_instances
            updatedMap["dedicated_hosts"] = ec2ExtendedState!!.dedicated_hosts
            updatedMap["amis"] = ec2ExtendedState!!.amis
            updatedMap["ami_catalog"] = ec2ExtendedState!!.ami_catalog
        }
        updatedMap
    }

    val backendInstances by viewModel.ec2Instances.collectAsState()

    val instancesList = remember(backendInstances, selectedRegion, regionCode) {
        if (backendInstances.isNotEmpty()) {
            backendInstances.map { inst ->
                val prettyName = if (inst.instanceId == "i-06d74665d9e16da17") "Aws_Mobile_App"
                                else if (inst.instanceId == "i-0f8a927a4d531a7bc") "Aws_Prod_Database"
                                else if (inst.instanceId == "i-0a2b8cd9e8f471a2a") "Aws_Cache_Cluster"
                                else "Instance - " + inst.instanceId.takeLast(6)
                AwsEc2Instance(
                    id = inst.instanceId,
                    name = prettyName,
                    state = inst.state.replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.getDefault()) else it.toString() },
                    type = inst.instanceType,
                    statusCheck = if (inst.state.equals("running", ignoreCase = true)) "Passed" else "-",
                    az = "${inst.region}a",
                    publicDns = if (!inst.publicIp.isNullOrBlank()) "ec2-${inst.publicIp.replace(".", "-")}.compute.amazonaws.com" else "-",
                    publicIp = inst.publicIp ?: "-",
                    privateIp = inst.privateIp ?: "-",
                    elasticIp = "-",
                    ipv6 = "-",
                    monitoring = "disabled",
                    securityGroup = "default",
                    keyPair = "None",
                    launchTime = "Just scanned",
                    platform = "Linux/UNIX",
                    iamRole = "None",
                    vpcId = "vpc-default",
                    subnetId = "subnet-default"
                )
            }
        } else {
            val totalCount = counts["instances"] ?: 2
            val runningCount = counts["instances_running"] ?: 1
            val list = mutableListOf<AwsEc2Instance>()
            for (i in 0 until totalCount) {
                val isRunning = i < runningCount
                val name = if (i == 0) "Aws_Mobile_App" else if (i == 1) "Aws_Prod_Database" else "Aws_Cache_Cluster"
                val id = if (i == 0) "i-06d74665d9e16da17" else if (i == 1) "i-0f8a927a4d531a7bc" else "i-0a2b8cd9e8f471a2a"
                val state = if (isRunning) "Running" else "Stopped"
                val type = if (i == 0) "t2.medium" else if (i == 1) "t3.large" else "t3.medium"
                val status = if (isRunning) "Passed" else "-"
                val azSuffix = if (i == 0) "d" else if (i == 1) "a" else "b"
                val publicIp = if (i == 0) "54.205.123.215" else if (i == 1) "34.210.44.12" else "52.90.11.168"
                val privateIp = if (i == 0) "10.0.1.53" else if (i == 1) "10.0.2.14" else "10.0.3.9"
                val elasticIp = if (i == 0) "54.205.123.215" else "-"
                val monitoring = if (i == 1) "enabled" else "disabled"
                val sg = if (i == 0) "launch-wizard-13" else if (i == 1) "db-secure-sg" else "redis-sg"
                val key = if (i == 0) "aws-mobile-app" else if (i == 1) "aws-prod-key" else "aws-cache-key"
                val launch = if (i == 0) "2026/06/16 12:49 GMT+5:30" else if (i == 1) "2026/06/15 08:30 GMT+5:30" else "2026/06/16 01:15 GMT+5:30"
                
                list.add(
                    AwsEc2Instance(
                        id = id,
                        name = name,
                        state = state,
                        type = type,
                        statusCheck = status,
                        az = "$regionCode$azSuffix",
                        publicDns = "ec2-${publicIp.replace(".", "-")}.compute.amazonaws.com",
                        publicIp = publicIp,
                        privateIp = privateIp,
                        elasticIp = elasticIp,
                        ipv6 = "-",
                        monitoring = monitoring,
                        securityGroup = sg,
                        keyPair = key,
                        launchTime = launch,
                        platform = "Linux/UNIX",
                        iamRole = if (i == 1) "RDS-Service-Role" else "None",
                        vpcId = "vpc-018274718cd992ab2",
                        subnetId = "subnet-0a8163f92de22bc71"
                    )
                )
            }
            list
        }
    }

    val instanceStatesMap = remember(instancesList) {
        mutableStateMapOf<String, String>().apply {
            instancesList.forEach { put(it.id, it.state) }
        }
    }

    val awsHeaderBg = if (isDarkTheme) Color(0xFF16191F) else Color(0xFF1C273A)
    val awsWorkspaceBg = if (isDarkTheme) Color(0xFF0F1115) else Color(0xFFF2F3F3)
    val awsSidebarBg = if (isDarkTheme) Color(0xFF1E222B) else Color(0xFFFAFAFA)
    val awsRowBg = if (isDarkTheme) Color(0xFF1A1D24) else Color(0xFFFFFFFF)
    val awsRowSelectedBg = if (isDarkTheme) Color(0xFF1D2D3A) else Color(0xFFEBF5FC)
    val awsTableHeaderBg = if (isDarkTheme) Color(0xFF22262F) else Color(0xFFFAFAFA)
    val awsBorderColor = if (isDarkTheme) Color(0xFF2D3340) else Color(0xFFEAEDED)
    val awsTextPrimary = if (isDarkTheme) Color(0xFFF1F3F5) else Color(0xFF111111)
    val awsTextSecondary = if (isDarkTheme) Color(0xFFA1B0CB) else Color(0xFF555555)
    val awsBlueText = if (isDarkTheme) Color(0xFF4DA4FF) else Color(0xFF0066CC)
    val awsOrange = Color(0xFFEC7211)

    if (viewMode == "aws_console") {
        var isSidebarExpanded by remember { mutableStateOf(false) }
        val selectedInstance = instancesList.find { it.id == selectedInstanceId }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(awsWorkspaceBg)
        ) {
            // --- AWS HEADER BAR ---
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .background(awsHeaderBg)
                    .padding(horizontal = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // AWS Logo
                Column(
                    modifier = Modifier.clickable { viewMode = "grid" },
                    horizontalAlignment = Alignment.Start
                ) {
                    Text(
                        text = "aws",
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 18.sp,
                        color = Color.White
                    )
                    Box(
                        modifier = Modifier
                            .width(22.dp)
                            .height(2.dp)
                            .background(awsOrange)
                    )
                }

                Spacer(modifier = Modifier.width(16.dp))

                // Search field (mock)
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .height(30.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(if (isDarkTheme) Color(0xFF2A2D35) else Color(0xFF2D3C53))
                        .padding(horizontal = 8.dp),
                    contentAlignment = Alignment.CenterStart
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = "Search icon",
                            tint = Color.LightGray,
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Search (Alt+S)",
                            color = Color.LightGray,
                            fontSize = 11.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                // User / Region indicators
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(3.dp))
                            .background(if (isDarkTheme) Color(0xFF2E333D) else Color(0xFF2B3A50))
                            .padding(horizontal = 6.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = regionCode.uppercase(),
                            color = Color.White,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                    }

                    Box(
                        modifier = Modifier
                            .size(24.dp)
                            .clip(CircleShape)
                            .background(Color.Gray),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("K", color = Color.White, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            // --- AWS SUB-HEADER (Breadcrumbs & Hamburger) ---
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(40.dp)
                    .background(if (isDarkTheme) Color(0xFF1E222B) else Color.White)
                    .drawBehind {
                        drawLine(
                            color = awsBorderColor,
                            start = Offset(0f, size.height),
                            end = Offset(size.width, size.height),
                            strokeWidth = 1.dp.toPx()
                        )
                    }
                    .padding(horizontal = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(
                    onClick = { viewMode = "grid" },
                    modifier = Modifier.size(28.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Exit AWS Console",
                        tint = awsTextPrimary,
                        modifier = Modifier.size(16.dp)
                    )
                }

                Spacer(modifier = Modifier.width(4.dp))

                Box(
                    modifier = Modifier
                        .size(28.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(if (isSidebarExpanded) awsRowSelectedBg else Color.Transparent)
                        .clickable { isSidebarExpanded = !isSidebarExpanded }
                        .padding(4.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Menu,
                        contentDescription = "Toggle Navigation Menu",
                        tint = if (isSidebarExpanded) awsBlueText else awsTextPrimary,
                        modifier = Modifier.size(18.dp)
                    )
                }

                Spacer(modifier = Modifier.width(8.dp))

                Text(
                    text = "EC2",
                    fontSize = 12.sp,
                    color = awsBlueText,
                    fontWeight = FontWeight.SemiBold
                )
                Icon(
                    imageVector = Icons.Default.ChevronRight,
                    contentDescription = ">",
                    tint = awsTextSecondary,
                    modifier = Modifier.size(12.dp)
                )
                Text(
                    text = activeConsoleTab,
                    fontSize = 12.sp,
                    color = awsTextPrimary,
                    fontWeight = FontWeight.Bold
                )
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) {
                Row(modifier = Modifier.fillMaxSize()) {
                    // --- SIDE NAVIGATION DRAWER (COLLAPSIBLE) ---
                    AnimatedVisibility(
                        visible = isSidebarExpanded,
                        enter = slideInHorizontally() + fadeIn(),
                        exit = slideOutHorizontally() + fadeOut()
                    ) {
                        Column(
                            modifier = Modifier
                                .width(180.dp)
                                .fillMaxHeight()
                                .background(awsSidebarBg)
                                .drawBehind {
                                    drawLine(
                                        color = awsBorderColor,
                                        start = Offset(size.width, 0f),
                                        end = Offset(size.width, size.height),
                                        strokeWidth = 1.dp.toPx()
                                    )
                                }
                                .verticalScroll(rememberScrollState())
                                .padding(vertical = 8.dp)
                        ) {
                            Text(
                                text = "EC2 Dashboard",
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { isSidebarExpanded = false }
                                    .padding(horizontal = 16.dp, vertical = 6.dp),
                                fontSize = 11.sp,
                                color = awsTextPrimary
                            )
                            Text(
                                text = "Events",
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 16.dp, vertical = 6.dp),
                                fontSize = 11.sp,
                                color = awsTextSecondary
                            )
                            val drawerItems = listOf(
                                "Instances" to listOf("Instances", "Instance Types", "Launch Templates", "Spot Requests", "Savings Plans", "Reserved Instances", "Dedicated Hosts", "Capacity Reservations", "Capacity Manager")
                            )
                            drawerItems.forEach { (category, items) ->
                                items.forEach { item ->
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .background(if (activeConsoleTab == item) awsRowSelectedBg else Color.Transparent)
                                            .clickable {
                                                activeConsoleTab = item
                                            }
                                            .padding(horizontal = 16.dp, vertical = 6.dp)
                                    ) {
                                        Text(
                                            text = item,
                                            fontSize = 11.sp,
                                            fontWeight = if (activeConsoleTab == item) FontWeight.Bold else FontWeight.Normal,
                                            color = if (activeConsoleTab == item) awsBlueText else awsTextSecondary
                                        )
                                    }
                                }
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Images",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = awsTextPrimary,
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                            )
                            listOf("AMIs", "AMI Catalog").forEach { item ->
                                Text(
                                    text = item,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(horizontal = 16.dp, vertical = 4.dp),
                                    fontSize = 11.sp,
                                    color = awsTextSecondary
                                )
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Elastic Block Store",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = awsTextPrimary,
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                            )
                            listOf("Volumes", "Snapshots", "Lifecycle Manager").forEach { item ->
                                Text(
                                    text = item,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(horizontal = 16.dp, vertical = 4.dp),
                                    fontSize = 11.sp,
                                    color = awsTextSecondary
                                )
                            }
                        }
                    }

                    // --- MAIN WORKSPACE VIEW ---
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .fillMaxHeight()
                            .verticalScroll(rememberScrollState())
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        if (activeConsoleTab == "Instances") {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Instances (${instancesList.size})",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                color = awsTextPrimary
                            )

                            Text(
                                text = "Info",
                                fontSize = 11.sp,
                                color = awsBlueText,
                                modifier = Modifier.clickable { }
                            )
                        }

                        // --- ACTION BUTTONS ROW ---
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Button(
                                onClick = { },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (isDarkTheme) Color(0xFF2D3340) else Color.White,
                                    contentColor = awsTextPrimary
                                ),
                                border = BorderStroke(1.dp, awsBorderColor),
                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                                shape = RoundedCornerShape(4.dp),
                                modifier = Modifier.height(28.dp)
                            ) {
                                Text("Connect", fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                            }

                            Box {
                                Button(
                                    onClick = { isStateDropdownExpanded = true },
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = if (isDarkTheme) Color(0xFF2D3340) else Color.White,
                                        contentColor = awsTextPrimary
                                    ),
                                    border = BorderStroke(1.dp, awsBorderColor),
                                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                                    shape = RoundedCornerShape(4.dp),
                                    modifier = Modifier.height(28.dp)
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Text("Instance state", fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                                        Spacer(modifier = Modifier.width(2.dp))
                                        Icon(
                                            imageVector = Icons.Default.ArrowDropDown,
                                            contentDescription = "Dropdown",
                                            modifier = Modifier.size(14.dp)
                                        )
                                    }
                                }

                                DropdownMenu(
                                    expanded = isStateDropdownExpanded,
                                    onDismissRequest = { isStateDropdownExpanded = false },
                                    modifier = Modifier.background(awsRowBg).border(1.dp, awsBorderColor)
                                ) {
                                    DropdownMenuItem(
                                        text = { Text("Start instance", fontSize = 12.sp, color = awsTextPrimary) },
                                        onClick = {
                                            isStateDropdownExpanded = false
                                            selectedInstanceId?.let { id ->
                                                viewModel.startInstance(id)
                                                instanceStatesMap[id] = "Pending"
                                            }
                                        },
                                        enabled = selectedInstanceId != null && instanceStatesMap[selectedInstanceId] == "Stopped"
                                    )
                                    DropdownMenuItem(
                                        text = { Text("Stop instance", fontSize = 12.sp, color = awsTextPrimary) },
                                        onClick = {
                                            isStateDropdownExpanded = false
                                            selectedInstanceId?.let { id ->
                                                viewModel.stopInstance(id)
                                                instanceStatesMap[id] = "Stopping"
                                            }
                                        },
                                        enabled = selectedInstanceId != null && instanceStatesMap[selectedInstanceId] == "Running"
                                    )
                                    DropdownMenuItem(
                                        text = { Text("Reboot instance", fontSize = 12.sp, color = awsTextPrimary) },
                                        onClick = {
                                            isStateDropdownExpanded = false
                                            selectedInstanceId?.let { id ->
                                                viewModel.rebootInstance(id)
                                            }
                                        },
                                        enabled = selectedInstanceId != null && instanceStatesMap[selectedInstanceId] == "Running"
                                    )
                                    DropdownMenuItem(
                                        text = { Text("Terminate instance", fontSize = 12.sp, color = awsTextPrimary) },
                                        onClick = {
                                            isStateDropdownExpanded = false
                                            selectedInstanceId?.let { id ->
                                                instanceStatesMap[id] = "Terminated"
                                            }
                                        },
                                        enabled = selectedInstanceId != null && instanceStatesMap[selectedInstanceId] != "Terminated"
                                    )
                                }
                            }

                            Button(
                                onClick = { },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (isDarkTheme) Color(0xFF2D3340) else Color.White,
                                    contentColor = awsTextPrimary
                                ),
                                border = BorderStroke(1.dp, awsBorderColor),
                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                                shape = RoundedCornerShape(4.dp),
                                modifier = Modifier.height(28.dp)
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text("Actions", fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                                    Spacer(modifier = Modifier.width(2.dp))
                                    Icon(
                                        imageVector = Icons.Default.ArrowDropDown,
                                        contentDescription = "Dropdown",
                                        modifier = Modifier.size(14.dp)
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.weight(1f))

                            Button(
                                onClick = { },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = awsOrange,
                                    contentColor = Color.White
                                ),
                                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                                shape = RoundedCornerShape(4.dp),
                                modifier = Modifier.height(28.dp)
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text("Launch instances", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                    Spacer(modifier = Modifier.width(2.dp))
                                    Icon(
                                        imageVector = Icons.Default.ArrowDropDown,
                                        contentDescription = "Dropdown",
                                        modifier = Modifier.size(14.dp),
                                        tint = Color.White
                                    )
                                }
                            }
                        }

                        OutlinedTextField(
                            value = searchInput,
                            onValueChange = { searchInput = it },
                            placeholder = { Text("Find Instance by attribute or tag (case-sensitive)", fontSize = 11.sp) },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(38.dp),
                            textStyle = androidx.compose.ui.text.TextStyle(fontSize = 11.sp),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = awsBlueText,
                                unfocusedBorderColor = awsBorderColor,
                                focusedContainerColor = awsRowBg,
                                unfocusedContainerColor = awsRowBg
                            ),
                            leadingIcon = {
                                Icon(
                                    imageVector = Icons.Default.Search,
                                    contentDescription = "Search input",
                                    tint = awsTextSecondary,
                                    modifier = Modifier.size(14.dp)
                                )
                            },
                            singleLine = true
                        )

                        // --- THE HORIZONTALLY SCROLLABLE TABLE ---
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .border(1.dp, awsBorderColor, RoundedCornerShape(4.dp))
                                .background(awsRowBg)
                        ) {
                            Column(
                                modifier = Modifier.horizontalScroll(scrollState)
                            ) {
                                Row(
                                    modifier = Modifier
                                        .background(awsTableHeaderBg)
                                        .drawBehind {
                                            drawLine(
                                                color = awsBorderColor,
                                                start = Offset(0f, size.height),
                                                end = Offset(size.width, size.height),
                                                strokeWidth = 1.dp.toPx()
                                            )
                                        }
                                        .padding(vertical = 8.dp, horizontal = 4.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Box(modifier = Modifier.width(36.dp))
                                    TableHeaderCell("Name", 120.dp)
                                    TableHeaderCell("Instance ID", 150.dp)
                                    TableHeaderCell("Instance state", 100.dp)
                                    TableHeaderCell("Instance type", 100.dp)
                                    TableHeaderCell("Status check", 100.dp)
                                    TableHeaderCell("Availability Zone", 120.dp)
                                    TableHeaderCell("Public IPv4 DNS", 250.dp)
                                    TableHeaderCell("Public IPv4 address", 130.dp)
                                    TableHeaderCell("Elastic IP", 120.dp)
                                    TableHeaderCell("IPv6 IPs", 80.dp)
                                    TableHeaderCell("Monitoring", 90.dp)
                                    TableHeaderCell("Security group name", 150.dp)
                                    TableHeaderCell("Key name", 130.dp)
                                    TableHeaderCell("Launch time", 180.dp)
                                    TableHeaderCell("Platform", 100.dp)
                                }

                                val filteredInstances = instancesList.filter {
                                    searchInput.isEmpty() ||
                                    it.name.contains(searchInput, ignoreCase = true) ||
                                    it.id.contains(searchInput, ignoreCase = true) ||
                                    it.type.contains(searchInput, ignoreCase = true)
                                }

                                if (filteredInstances.isEmpty()) {
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(24.dp),
                                        horizontalArrangement = Arrangement.Center
                                    ) {
                                        Text("No matching instances pool found in $regionFullName.", fontSize = 11.sp, color = awsTextSecondary)
                                    }
                                } else {
                                    filteredInstances.forEach { instance ->
                                        val isCurrentSelected = selectedInstanceId == instance.id
                                        val currentState = instanceStatesMap[instance.id] ?: instance.state

                                        Row(
                                            modifier = Modifier
                                                .background(if (isCurrentSelected) awsRowSelectedBg else awsRowBg)
                                                .clickable {
                                                    selectedInstanceId = if (isCurrentSelected) null else instance.id
                                                }
                                                .drawBehind {
                                                    drawLine(
                                                        color = awsBorderColor,
                                                        start = Offset(0f, size.height),
                                                        end = Offset(size.width, size.height),
                                                        strokeWidth = 0.5.dp.toPx()
                                                    )
                                                }
                                                .padding(vertical = 8.dp, horizontal = 4.dp),
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Box(
                                                modifier = Modifier.width(36.dp),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Checkbox(
                                                    checked = isCurrentSelected,
                                                    onCheckedChange = { checked ->
                                                        selectedInstanceId = if (checked) instance.id else null
                                                    },
                                                    colors = CheckboxDefaults.colors(
                                                        checkedColor = awsBlueText,
                                                        uncheckedColor = awsTextSecondary
                                                    )
                                                )
                                            }

                                            TableCell(instance.name, 120.dp, awsTextPrimary)

                                            TableCellClickable(instance.id, 150.dp, awsBlueText) {
                                                selectedInstanceId = if (isCurrentSelected) null else instance.id
                                            }

                                            Row(
                                                modifier = Modifier.width(100.dp),
                                                verticalAlignment = Alignment.CenterVertically,
                                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                                            ) {
                                                val stateDotColor = when (currentState) {
                                                    "Running" -> BentoTermGreen
                                                    "Stopped" -> Color.Gray
                                                    "Terminated" -> BentoAccentRed
                                                    "Pending", "Stopping" -> Color(0xFFEC7211)
                                                    else -> Color.Gray
                                                }
                                                Box(
                                                    modifier = Modifier
                                                        .size(8.dp)
                                                        .clip(CircleShape)
                                                        .background(stateDotColor)
                                                )
                                                Text(
                                                    text = currentState,
                                                    fontSize = 11.sp,
                                                    color = awsTextPrimary,
                                                    fontFamily = FontFamily.Monospace
                                                )
                                            }

                                            TableCell(instance.type, 100.dp, awsTextPrimary)
                                            TableCell(instance.statusCheck, 100.dp, awsTextPrimary)
                                            TableCell(instance.az, 120.dp, awsTextPrimary)
                                            TableCell(instance.publicDns, 250.dp, awsTextPrimary)
                                            TableCell(instance.publicIp, 130.dp, awsTextPrimary)
                                            TableCell(instance.elasticIp, 120.dp, awsTextPrimary)
                                            TableCell(instance.ipv6, 80.dp, awsTextPrimary)
                                            TableCell(instance.monitoring, 90.dp, awsTextPrimary)
                                            TableCell(instance.securityGroup, 150.dp, awsTextPrimary)
                                            TableCell(instance.keyPair, 130.dp, awsTextPrimary)
                                            TableCell(instance.launchTime, 180.dp, awsTextPrimary)
                                            TableCell(instance.platform, 100.dp, awsTextPrimary)
                                        }
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(6.dp))

                        // --- BOTTOM DETAIL SECTION ---
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .border(1.dp, awsBorderColor, RoundedCornerShape(4.dp)),
                            colors = CardDefaults.cardColors(
                                containerColor = awsRowBg
                            ),
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Column(
                                modifier = Modifier.padding(12.dp)
                            ) {
                                if (selectedInstance == null) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Text(
                                            text = "Select an instance",
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = awsTextPrimary
                                        )
                                        Icon(
                                            imageVector = Icons.Default.Settings,
                                            contentDescription = "Config details",
                                            tint = awsTextSecondary,
                                            modifier = Modifier.size(16.dp)
                                        )
                                    }
                                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp), color = awsBorderColor)
                                    Text(
                                        text = "To view details of an instance, select its checkbox or click on its row.",
                                        fontSize = 11.sp,
                                        color = awsTextSecondary
                                    )
                                } else {
                                    val currentState = instanceStatesMap[selectedInstance.id] ?: selectedInstance.state
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Column {
                                            Text(
                                                text = "Instance: ${selectedInstance.id} (${selectedInstance.name})",
                                                fontSize = 13.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = awsTextPrimary
                                            )
                                            Text(
                                                text = "Public IP: ${selectedInstance.publicIp} | State: ${currentState}",
                                                fontSize = 10.sp,
                                                color = awsTextSecondary
                                            )
                                        }

                                        IconButton(
                                            onClick = { selectedInstanceId = null },
                                            modifier = Modifier.size(24.dp)
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Close,
                                                contentDescription = "Close details",
                                                tint = awsTextSecondary,
                                                modifier = Modifier.size(14.dp)
                                            )
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(10.dp))

                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .horizontalScroll(rememberScrollState()),
                                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                                    ) {
                                        listOf("Details", "Security", "Networking", "Storage", "Status checks", "Monitoring", "Tags").forEach { tab ->
                                            val isTabSelected = selectedTabInDetails == tab
                                            Column(
                                                modifier = Modifier
                                                    .clickable { selectedTabInDetails = tab }
                                                    .padding(vertical = 4.dp),
                                                horizontalAlignment = Alignment.CenterHorizontally
                                            ) {
                                                Text(
                                                    text = tab,
                                                    fontSize = 11.sp,
                                                    fontWeight = if (isTabSelected) FontWeight.Bold else FontWeight.SemiBold,
                                                    color = if (isTabSelected) awsBlueText else awsTextSecondary
                                                )
                                                if (isTabSelected) {
                                                    Box(
                                                        modifier = Modifier
                                                            .width(28.dp)
                                                            .height(2.dp)
                                                            .background(awsBlueText)
                                                    )
                                                }
                                            }
                                        }
                                    }

                                    HorizontalDivider(modifier = Modifier.padding(vertical = 6.dp), color = awsBorderColor)

                                    when (selectedTabInDetails) {
                                        "Details" -> {
                                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                                    DetailItem("Instance ID", selectedInstance.id, Modifier.weight(1f), awsTextPrimary, awsTextSecondary, awsBlueText)
                                                    DetailItem("Instance state", currentState, Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                }
                                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                                    DetailItem("Instance type", selectedInstance.type, Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                    DetailItem("Private IPv4 Address", selectedInstance.privateIp, Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                }
                                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                                    DetailItem("VPC ID", selectedInstance.vpcId, Modifier.weight(1f), awsTextPrimary, awsTextSecondary, awsBlueText)
                                                    DetailItem("Subnet ID", selectedInstance.subnetId, Modifier.weight(1f), awsTextPrimary, awsTextSecondary, awsBlueText)
                                                }
                                                Row(modifier = Modifier.fillMaxWidth()) {
                                                    DetailItem("Public IPv4 DNS", selectedInstance.publicDns, Modifier.fillMaxWidth(), awsTextPrimary, awsTextSecondary)
                                                }
                                            }
                                        }
                                        "Security" -> {
                                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                                Text("Security Groups: ${selectedInstance.securityGroup}", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = awsTextPrimary)
                                                Text("Inbound Active Firewall Security Rules:", fontSize = 10.sp, fontWeight = FontWeight.SemiBold, color = awsTextSecondary)
                                                Box(
                                                    modifier = Modifier
                                                        .fillMaxWidth()
                                                        .border(1.dp, awsBorderColor, RoundedCornerShape(3.dp))
                                                        .background(awsTableHeaderBg)
                                                        .padding(8.dp)
                                                ) {
                                                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                                        Text("• TCP Port 22 (SSH) - Source: 0.0.0.0/0 (Active)", fontSize = 10.sp, color = BentoTermGreen, fontFamily = FontFamily.Monospace)
                                                        Text("• TCP Port 80 (HTTP) - Source: 0.0.0.0/0 (Active)", fontSize = 10.sp, color = BentoTermGreen, fontFamily = FontFamily.Monospace)
                                                        Text("• TCP Port 443 (HTTPS) - Source: 0.0.0.0/0 (Active)", fontSize = 10.sp, color = BentoTermGreen, fontFamily = FontFamily.Monospace)
                                                    }
                                                }
                                            }
                                        }
                                        "Networking" -> {
                                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                                    DetailItem("Network interface", "eth0", Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                    DetailItem("Public IPv4", selectedInstance.publicIp, Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                }
                                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                                    DetailItem("Private IPv4", selectedInstance.privateIp, Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                    DetailItem("Elastic IP", selectedInstance.elasticIp, Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                }
                                            }
                                        }
                                        "Storage" -> {
                                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                                Text("Root Device: /dev/xvda", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = awsTextPrimary)
                                                Text("Attached Block Device Volumes list:", fontSize = 10.sp, color = awsTextSecondary)
                                                Box(
                                                    modifier = Modifier
                                                        .fillMaxWidth()
                                                        .border(1.dp, awsBorderColor, RoundedCornerShape(2.dp))
                                                        .background(awsTableHeaderBg)
                                                        .padding(8.dp)
                                                ) {
                                                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                                        Text("vol-078a9c2b48 | gp3 | /dev/xvda | size: 8 GiB", fontSize = 11.sp, color = awsTextPrimary, fontFamily = FontFamily.Monospace)
                                                        Text("Attached (100%)", fontSize = 11.sp, color = BentoTermGreen, fontFamily = FontFamily.Monospace)
                                                    }
                                                }
                                            }
                                        }
                                        "Status checks" -> {
                                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                                Text("Status Check Status: ${if(currentState == "Running") "2/2 checks passed" else "Not Available"}", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = awsTextPrimary)
                                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                                    DetailItem("System status", if(currentState == "Running") "Passed" else "-", Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                    DetailItem("Instance status", if(currentState == "Running") "Passed" else "-", Modifier.weight(1f), awsTextPrimary, awsTextSecondary)
                                                }
                                            }
                                        }
                                        "Monitoring" -> {
                                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                                Text("CloudWatch Basic Monitoring: disabled", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = awsTextPrimary)
                                                Text("Detailed monitoring can be enabled under Amazon CloudWatch configurations.", fontSize = 10.sp, color = awsTextSecondary)
                                            }
                                        }
                                        "Tags" -> {
                                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                                Text("Configured Metadata Tags (${if (selectedInstance.id == "i-06d74665d9e16da17") 3 else 2}):", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = awsTextPrimary)
                                                Box(
                                                    modifier = Modifier
                                                        .fillMaxWidth()
                                                        .border(1.dp, awsBorderColor, RoundedCornerShape(2.dp))
                                                        .background(awsTableHeaderBg)
                                                        .padding(8.dp)
                                                ) {
                                                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                                        Text("• Name = ${selectedInstance.name}", fontSize = 10.sp, color = awsTextPrimary, fontFamily = FontFamily.Monospace)
                                                        Text("• Environment = Development", fontSize = 10.sp, color = awsTextPrimary, fontFamily = FontFamily.Monospace)
                                                        if (selectedInstance.id == "i-06d74665d9e16da17") {
                                                            Text("• Project = Gemini-AWS-Sync", fontSize = 10.sp, color = awsTextPrimary, fontFamily = FontFamily.Monospace)
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        } else if (activeConsoleTab == "Instance Types") {
                            Text(
                                text = "Instance Types",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                color = awsTextPrimary
                            )
                            Spacer(modifier = Modifier.height(10.dp))
                            
                            // Mock Instance Types table
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .border(1.dp, awsBorderColor, RoundedCornerShape(4.dp))
                                    .background(awsRowBg)
                            ) {
                                Column(
                                    modifier = Modifier.horizontalScroll(scrollState)
                                ) {
                                    Row(
                                        modifier = Modifier
                                            .background(awsTableHeaderBg)
                                            .drawBehind {
                                                drawLine(
                                                    color = awsBorderColor,
                                                    start = Offset(0f, size.height),
                                                    end = Offset(size.width, size.height),
                                                    strokeWidth = 1.dp.toPx()
                                                )
                                            }
                                            .padding(vertical = 8.dp, horizontal = 4.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Box(modifier = Modifier.width(36.dp))
                                        TableHeaderCell("Instance Type", 150.dp)
                                        TableHeaderCell("vCPUs", 80.dp)
                                        TableHeaderCell("Memory (GiB)", 100.dp)
                                        TableHeaderCell("Instance Storage (GB)", 150.dp)
                                        TableHeaderCell("Network Performance", 150.dp)
                                    }
                                    
                                    val dummyInstanceTypes = listOf(
                                        listOf("t2.micro", "1", "1", "EBS only", "Low to Moderate"),
                                        listOf("t3.micro", "2", "1", "EBS only", "Up to 5 Gigabit"),
                                        listOf("m5.large", "2", "8", "EBS only", "Up to 10 Gigabit"),
                                        listOf("c5.xlarge", "4", "8", "EBS only", "Up to 10 Gigabit")
                                    )
                                    
                                    dummyInstanceTypes.forEach { typeData ->
                                        Row(
                                            modifier = Modifier
                                                .background(awsRowBg)
                                                .drawBehind {
                                                    drawLine(
                                                        color = awsBorderColor,
                                                        start = Offset(0f, size.height),
                                                        end = Offset(size.width, size.height),
                                                        strokeWidth = 0.5.dp.toPx()
                                                    )
                                                }
                                                .padding(vertical = 8.dp, horizontal = 4.dp),
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Box(
                                                modifier = Modifier.width(36.dp),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Checkbox(
                                                    checked = false,
                                                    onCheckedChange = {},
                                                    colors = CheckboxDefaults.colors(
                                                        checkedColor = awsBlueText,
                                                        uncheckedColor = awsTextSecondary
                                                    )
                                                )
                                            }
                                            
                                            TableCell(typeData[0], 150.dp, awsBlueText)
                                            TableCell(typeData[1], 80.dp, awsTextPrimary)
                                            TableCell(typeData[2], 100.dp, awsTextPrimary)
                                            TableCell(typeData[3], 150.dp, awsTextPrimary)
                                            TableCell(typeData[4], 150.dp, awsTextPrimary)
                                        }
                                    }
                                }
                            }
                        } else if (activeConsoleTab == "Launch Templates") {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "Launch Templates (1)",
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = awsTextPrimary
                                )
                                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    IconButton(
                                        onClick = {},
                                        modifier = Modifier.size(32.dp).border(1.dp, awsBorderColor, RoundedCornerShape(4.dp))
                                    ) {
                                        Icon(Icons.Default.Refresh, contentDescription = "Refresh", tint = awsBlueText, modifier = Modifier.size(16.dp))
                                    }
                                    
                                    Box(
                                        modifier = Modifier
                                            .border(1.dp, awsBorderColor, RoundedCornerShape(16.dp))
                                            .background(if (isDarkTheme) Color(0xFF1E1E1E) else Color.White, RoundedCornerShape(16.dp))
                                            .padding(horizontal = 12.dp, vertical = 6.dp)
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Text("Actions", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = awsBlueText)
                                            Icon(Icons.Default.ArrowDropDown, contentDescription = null, modifier = Modifier.size(16.dp), tint = awsBlueText)
                                        }
                                    }

                                    Box(
                                        modifier = Modifier
                                            .background(awsOrange, RoundedCornerShape(16.dp))
                                            .padding(horizontal = 12.dp, vertical = 6.dp)
                                            .clickable { }
                                    ) {
                                        Text("Create launch template", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = if (isDarkTheme) Color.White else Color.Black)
                                    }
                                }
                            }
                            Spacer(modifier = Modifier.height(10.dp))
                            
                            // Mock Launch Templates table
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .border(1.dp, awsBorderColor, RoundedCornerShape(4.dp))
                                    .background(awsRowBg)
                            ) {
                                Column(
                                    modifier = Modifier.horizontalScroll(scrollState)
                                ) {
                                    Row(
                                        modifier = Modifier
                                            .background(awsTableHeaderBg)
                                            .drawBehind {
                                                drawLine(
                                                    color = awsBorderColor,
                                                    start = Offset(0f, size.height),
                                                    end = Offset(size.width, size.height),
                                                    strokeWidth = 1.dp.toPx()
                                                )
                                            }
                                            .padding(vertical = 8.dp, horizontal = 4.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Box(modifier = Modifier.width(36.dp))
                                        TableHeaderCell("Launch Template ID", 180.dp)
                                        TableHeaderCell("Launch Template Name", 180.dp)
                                        TableHeaderCell("Default Version", 100.dp)
                                        TableHeaderCell("Latest Version", 100.dp)
                                        TableHeaderCell("Create Time", 180.dp)
                                        TableHeaderCell("Created By", 250.dp)
                                        TableHeaderCell("Managed", 80.dp)
                                        TableHeaderCell("Operator", 80.dp)
                                    }
                                    
                                    val dummyLaunchTemplates = listOf(
                                        listOf("lt-067898a12b6e2d329", "demo-app-template", "1", "1", "2026-06-10T10:26:09.000Z", "arn:aws:iam::077660206700:root", "false", "-")
                                    )
                                    
                                    dummyLaunchTemplates.forEach { typeData ->
                                        Row(
                                            modifier = Modifier
                                                .background(awsRowBg)
                                                .drawBehind {
                                                    drawLine(
                                                        color = awsBorderColor,
                                                        start = Offset(0f, size.height),
                                                        end = Offset(size.width, size.height),
                                                        strokeWidth = 0.5.dp.toPx()
                                                    )
                                                }
                                                .padding(vertical = 8.dp, horizontal = 4.dp),
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Box(
                                                modifier = Modifier.width(36.dp),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Checkbox(
                                                    checked = false,
                                                    onCheckedChange = {},
                                                    colors = CheckboxDefaults.colors(
                                                        checkedColor = awsBlueText,
                                                        uncheckedColor = awsTextSecondary
                                                    )
                                                )
                                            }
                                            
                                            TableCell(typeData[0], 180.dp, awsBlueText)
                                            TableCell(typeData[1], 180.dp, awsTextPrimary)
                                            TableCell(typeData[2], 100.dp, awsTextPrimary)
                                            TableCell(typeData[3], 100.dp, awsTextPrimary)
                                            TableCell(typeData[4], 180.dp, awsTextPrimary)
                                            TableCell(typeData[5], 250.dp, awsTextPrimary)
                                            TableCell(typeData[6], 80.dp, awsTextPrimary)
                                            TableCell(typeData[7], 80.dp, awsTextPrimary)
                                        }
                                    }
                                }
                            }
                        } else {
                            Text(
                                text = "Content for $activeConsoleTab is not currently available in this preview.",
                                color = awsTextSecondary,
                                fontSize = 12.sp,
                                modifier = Modifier.padding(16.dp)
                            )
                        }
                    }
                }
            }
        }
    } else {
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

            // Launch Instance Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                    border = BorderStroke(1.dp, if (isDarkTheme) Color(0xFF2C2A35) else BentoBorderMedium),
                    colors = CardDefaults.cardColors(
                        containerColor = if (isDarkTheme) Color(0xFF151419) else Color.White
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = "Launch instance",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (isDarkTheme) Color.White else BentoTextDark
                        )
                        Text(
                            text = "To get started with EC2, you can launch an instance, which is a virtual server in the cloud.",
                            fontSize = 13.sp,
                            color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle,
                            lineHeight = 18.sp
                        )
                        Button(
                            onClick = { viewMode = "aws_console" },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFEC7211),
                                contentColor = Color.White
                            ),
                            shape = RoundedCornerShape(20.dp),
                            contentPadding = PaddingValues(horizontal = 24.dp, vertical = 12.dp)
                        ) {
                            Text(
                                text = "Launch instance",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }

            // Service Health Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                    border = BorderStroke(1.dp, if (isDarkTheme) Color(0xFF2C2A35) else BentoBorderMedium),
                    colors = CardDefaults.cardColors(
                        containerColor = if (isDarkTheme) Color(0xFF151419) else Color.White
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = "Service health",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (isDarkTheme) Color.White else BentoTextDark
                        )
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Icon(
                                imageVector = Icons.Default.CheckCircle,
                                contentDescription = "Healthy",
                                tint = BentoTermGreen,
                                modifier = Modifier.size(24.dp)
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Column {
                                Text(
                                    text = "Service is operating normally",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (isDarkTheme) BentoTermGreen else BentoTextDark
                                )
                                Text(
                                    text = "$regionFullName",
                                    fontSize = 12.sp,
                                    color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle
                                )
                            }
                        }
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
                                        .clickable { viewModel.refreshEC2CacheAndReload() }
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
                                ResourceGridItem("Instances (running)", counts["instances_running"] ?: 1, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Instances", counts["instances"] ?: 2, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Instance Types", counts["instance_types"] ?: 15, isDarkTheme) {
                                    activeConsoleTab = "Instance Types"
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Launch Templates", counts["launch_templates"] ?: 3, isDarkTheme) {
                                    activeConsoleTab = "Launch Templates"
                                    viewMode = "aws_console"
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Spot Requests", counts["spot_requests"] ?: 0, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Savings Plans", counts["savings_plans"] ?: 1, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Reserved Instances", counts["reserved_instances"] ?: 0, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Dedicated Hosts", counts["dedicated_hosts"] ?: 0, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Capacity Reservations", counts["capacity_reservations"] ?: 0, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Capacity Manager", counts["capacity_manager"] ?: 1, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
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
                                ResourceGridItem("AMIs", counts["amis"] ?: 2, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("AMI Catalog", counts["ami_catalog"] ?: 12, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
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
                                ResourceGridItem("Volumes", counts["volumes"] ?: 1, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Snapshots", counts["snapshots"] ?: 4, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Lifecycle Manager", counts["lifecycle_manager"] ?: 1, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
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
                                ResourceGridItem("Security Groups", counts["security_groups"] ?: 18, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Elastic IPs", counts["elastic_ips"] ?: 4, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Placement Groups", counts["placement_groups"] ?: 0, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Key Pairs", counts["key_pairs"] ?: 4, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Network Interfaces", counts["network_interfaces"] ?: 3, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
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
                                ResourceGridItem("Load Balancers", counts["load_balancers"] ?: 0, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Target Groups", counts["target_groups"] ?: 2, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(10.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Box(modifier = Modifier.weight(1f)) {
                                ResourceGridItem("Trust Stores", counts["trust_stores"] ?: 0, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
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
                                ResourceGridItem("Auto Scaling Groups", counts["auto_scaling"] ?: 0, isDarkTheme) {
                                    viewMode = "aws_console"
                                }
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

@Composable
fun TableHeaderCell(text: String, width: androidx.compose.ui.unit.Dp) {
    Box(
        modifier = Modifier
            .width(width)
            .padding(horizontal = 6.dp)
    ) {
        Text(
            text = text,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = Color.Gray,
            maxLines = 1
        )
    }
}

@Composable
fun TableCell(text: String, width: androidx.compose.ui.unit.Dp, color: Color) {
    Box(
        modifier = Modifier
            .width(width)
            .padding(horizontal = 6.dp)
    ) {
        Text(
            text = text,
            fontSize = 11.sp,
            color = color,
            fontFamily = FontFamily.Monospace,
            maxLines = 1
        )
    }
}

@Composable
fun TableCellClickable(text: String, width: androidx.compose.ui.unit.Dp, color: Color, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .width(width)
            .clickable { onClick() }
            .padding(horizontal = 6.dp)
    ) {
        Text(
            text = text,
            fontSize = 11.sp,
            color = color,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.Bold,
            maxLines = 1
        )
    }
}

@Composable
fun DetailItem(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    textColor: Color,
    labelColor: Color,
    linkColor: Color? = null
) {
    Column(modifier = modifier) {
        Text(
            text = label,
            fontSize = 9.sp,
            fontWeight = FontWeight.SemiBold,
            color = labelColor
        )
        Spacer(modifier = Modifier.height(2.dp))
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = value,
                fontSize = 11.sp,
                fontFamily = FontFamily.Monospace,
                color = linkColor ?: textColor,
                fontWeight = if (linkColor != null) FontWeight.Bold else FontWeight.Normal,
                modifier = Modifier.clickable(enabled = linkColor != null) { }
            )
        }
    }
}

data class AwsEc2Instance(
    val id: String,
    val name: String,
    val state: String,
    val type: String,
    val statusCheck: String,
    val az: String,
    val publicDns: String,
    val publicIp: String,
    val privateIp: String,
    val elasticIp: String,
    val ipv6: String,
    val monitoring: String,
    val securityGroup: String,
    val keyPair: String,
    val launchTime: String,
    val platform: String,
    val iamRole: String,
    val vpcId: String,
    val subnetId: String
)

