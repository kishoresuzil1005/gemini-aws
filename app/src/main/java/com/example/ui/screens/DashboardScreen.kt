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
                        Text(
                            text = "US-EAST-1",
                            color = BentoPurpleDark,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = "AWS Production Environment",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = BentoPurpleDark
                    )
                    Text(
                        text = if (isDiscovering) "Indexing EC2, RDS, and S3 assets in real-time..." else "Sync status: secured, indexing completed.",
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
                        // Avatar elements
                        Row(
                            horizontalArrangement = Arrangement.spacedBy((-6).dp)
                        ) {
                            val services = listOf("EC2", "RDS", "S3", "VPC")
                            services.forEach { service ->
                                Box(
                                    modifier = Modifier
                                        .size(34.dp)
                                        .clip(RoundedCornerShape(100.dp))
                                        .background(Color.White)
                                        .border(1.dp, BentoBorderLight, RoundedCornerShape(100.dp)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = service,
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
                                text = "nodes",
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
                                text = "Cost Efficiency Projection",
                                fontWeight = FontWeight.Bold,
                                color = BentoTextDark,
                                fontSize = 16.sp
                            )
                            Text(
                                text = "Multi-cloud optimization forecast models (USD)",
                                color = BentoTextSubtitle,
                                fontSize = 12.sp
                            )
                        }
                        Icon(
                            imageVector = Icons.Default.Leaderboard,
                            contentDescription = "Stats Chart",
                            tint = BentoPurplePrimary
                        )
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    // Draw custom multi-layer projection chart
                    MultiCloudProjectionChart()

                    Spacer(modifier = Modifier.height(16.dp))

                    // Legend markers
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        LegendItem(color = AWSColor, label = "Source (AWS)")
                        LegendItem(color = AzureColor, label = "Projected (Azure)")
                        LegendItem(color = BentoTermGreen, label = "Optimized (GCP)")
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
                    text = "Discovered Catalog (${resources.size})",
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

        items(resources.take(4)) { resource ->
            ResourceItemRow(resource = resource)
        }
    }
}

@Composable
fun MultiCloudProjectionChart() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(140.dp)
            .drawBehind {
                val width = size.width
                val height = size.height

                // Draw background grid lines (horizontal)
                val gridLines = 4
                for (i in 0..gridLines) {
                    val y = (height / gridLines) * i
                    drawLine(
                        color = BentoBorderMedium.copy(alpha = 0.4f),
                        start = Offset(0f, y),
                        end = Offset(width, y),
                        strokeWidth = 1f
                    )
                }

                // Values representing fictional costs
                val awsPoints = listOf(
                    Offset(0f, height * 0.82f),
                    Offset(width * 0.25f, height * 0.78f),
                    Offset(width * 0.5f, height * 0.81f),
                    Offset(width * 0.75f, height * 0.84f),
                    Offset(width, height * 0.88f)
                )

                val azurePoints = listOf(
                    Offset(0f, height * 0.82f),
                    Offset(width * 0.25f, height * 0.92f), 
                    Offset(width * 0.5f, height * 0.56f), 
                    Offset(width * 0.75f, height * 0.48f),
                    Offset(width, height * 0.44f)
                )

                val gcpPoints = listOf(
                    Offset(0f, height * 0.82f),
                    Offset(width * 0.25f, height * 0.65f),
                    Offset(width * 0.5f, height * 0.45f),
                    Offset(width * 0.75f, height * 0.32f),
                    Offset(width, height * 0.22f) 
                )

                // Draw Paths for line series
                fun drawTrendLine(points: List<Offset>, color: Color) {
                    val path = Path().apply {
                        moveTo(points[0].x, points[0].y)
                        for (i in 1 until points.size) {
                            cubicTo(
                                (points[i - 1].x + points[i].x) / 2, points[i - 1].y,
                                (points[i - 1].x + points[i].x) / 2, points[i].y,
                                points[i].x, points[i].y
                            )
                        }
                    }
                    drawPath(
                        path = path,
                        color = color,
                        style = Stroke(width = 3.dp.toPx())
                    )

                    // Draw points on vertices
                    points.forEach { point ->
                        drawCircle(
                            color = color,
                            radius = 6f,
                            center = point
                        )
                        drawCircle(
                            color = Color.White,
                            radius = 2.5f,
                            center = point
                        )
                    }
                }

                drawTrendLine(awsPoints, AWSColor)
                drawTrendLine(azurePoints, AzureColor)
                drawTrendLine(gcpPoints, BentoTermGreen)
            }
    )
}

@Composable
fun LegendItem(color: Color, label: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier = Modifier
                .size(10.dp)
                .clip(RoundedCornerShape(3.dp))
                .background(color)
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(text = label, color = BentoTextSubtitle, fontSize = 11.sp, fontWeight = FontWeight.Bold)
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
