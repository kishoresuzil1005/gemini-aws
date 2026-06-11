package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.Security
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
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.DiscoveryResource
import com.example.ui.CloudViewModel
import com.example.ui.theme.*
import java.util.Locale

@Composable
fun DependencyGraphScreen(
    viewModel: CloudViewModel,
    onNavigateToGenerator: () -> Unit,
    modifier: Modifier = Modifier
) {
    val resources by viewModel.resources.collectAsState()
    val selectedNode by viewModel.selectedGraphNode.collectAsState()
    val graphTopology by viewModel.graphTopology.collectAsState()
    val graphNodes = graphTopology?.nodes ?: emptyList()

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(SpaceSlate)
            .testTag("dependency_graph_screen")
    ) {
        if (resources.isEmpty()) {
            // Empty state UX compliance
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(32.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Default.Hub,
                    contentDescription = "No Graph Map Data",
                    tint = TextDim,
                    modifier = Modifier.size(64.dp)
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Topology Database Empty",
                    color = TextWhite,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Initiate a Cloud Discovery Scan in the Dashboard console first to populate Neo4j dependencies.",
                    color = TextDim,
                    fontSize = 14.sp,
                    textAlign = TextAlign.Center
                )
            }
        } else {
            // Main Canvas & Node container scrollable both vertically and horizontally
            val verticalScrollState = rememberScrollState()
            val horizontalScrollState = rememberScrollState()

            val edges = graphTopology?.edges ?: emptyList()
            val nodePositions = remember(graphNodes) {
                val map = mutableMapOf<String, Offset>()
                val count = graphNodes.size
                if (count > 0) {
                    val centerX = 500f
                    val centerY = 360f
                    val radius = 240f
                    graphNodes.forEachIndexed { i, node ->
                        val angle = (2 * Math.PI * i) / count
                        val x = centerX + radius * Math.cos(angle).toFloat()
                        val y = centerY + radius * Math.sin(angle).toFloat()
                        map[node.id] = Offset(x, y)
                    }
                }
                map
            }

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(verticalScrollState)
                    .horizontalScroll(horizontalScrollState)
            ) {
                // Background grid & linking dependency paths drawing scope
                Box(
                    modifier = Modifier
                        .size(width = 1000.dp, height = 720.dp)
                        .drawBehind {
                            fun drawDependencyCurve(start: Offset, end: Offset, color: Color) {
                                val path = Path().apply {
                                    moveTo(start.x, start.y)
                                    cubicTo(
                                        start.x, (start.y + end.y) / 2,
                                        end.x, (start.y + end.y) / 2,
                                        end.x, end.y
                                    )
                                }
                                drawPath(
                                    path = path,
                                    color = color.copy(alpha = 0.5f),
                                    style = Stroke(
                                        width = 2.dp.toPx()
                                    )
                                )
                            }

                            edges.forEach { edge ->
                                val startPos = nodePositions[edge.source]
                                val endPos = nodePositions[edge.target]
                                if (startPos != null && endPos != null) {
                                    drawDependencyCurve(
                                        Offset(startPos.x.dp.toPx(), startPos.y.dp.toPx()),
                                        Offset(endPos.x.dp.toPx(), endPos.y.dp.toPx()),
                                        CyberCyan
                                    )
                                }
                            }
                        }
                ) {
                    // Node Overlay Components with absolute positions matching the Canvas coordinates
                    graphNodes.forEach { node ->
                        val pos = nodePositions[node.id]
                        if (pos != null) {
                            val activeResource = resources.firstOrNull { it.id == node.id }
                                ?: DiscoveryResource(
                                    id = node.id, provider = "AWS", type = node.type,
                                    name = node.name, configurationHint = "",
                                    costEstimate = 0.0, dependenciesString = ""
                                )
                            GraphNodeItem(
                                resource = activeResource,
                                x = pos.x.toInt(),
                                y = pos.y.toInt(),
                                isSelected = selectedNode?.id == node.id,
                                onClick = { viewModel.selectGraphNode(it) }
                            )
                        }
                    }
                }
            }

            // Topology Zoom / Info Panel Floating Overlay Top Left
            Box(
                modifier = Modifier
                    .padding(16.dp)
                    .clip(RoundedCornerShape(6.dp))
                    .background(DeepCard.copy(alpha = 0.85f))
                    .border(1.dp, BorderGrey, RoundedCornerShape(6.dp))
                    .padding(horizontal = 12.dp, vertical = 6.dp)
                    .align(Alignment.TopStart)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Route, contentDescription = "Topology status", tint = CyberCyan, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Neo4j Topology Model: Active",
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                        color = TerminalGreen
                    )
                }
            }

            // Bottom Audit sliding detail panel for selected resource node
            AnimatedVisibility(
                visible = selectedNode != null,
                enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
                exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(),
                modifier = Modifier.align(Alignment.BottomCenter)
            ) {
                selectedNode?.let { node ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                            .testTag("node_audit_panel"),
                        border = BorderStroke(1.dp, CyberCyan),
                        colors = CardDefaults.cardColors(containerColor = SpaceSlate.copy(alpha = 0.95f))
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            // Title & Close Button
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        imageVector = Icons.Default.Analytics,
                                        contentDescription = "Audit Details",
                                        tint = CyberCyan
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = node.name,
                                        fontWeight = FontWeight.ExtraBold,
                                        fontSize = 18.sp,
                                        color = TextWhite
                                    )
                                }
                                IconButton(onClick = { viewModel.selectGraphNode(null) }) {
                                    Icon(Icons.Default.Close, contentDescription = "Close pane", tint = TextDim)
                                }
                            }

                            Divider(color = BorderGrey, modifier = Modifier.padding(vertical = 12.dp))

                            // Stats Grid
                            Row(modifier = Modifier.fillMaxWidth()) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text("RESOURCE TYPE", fontSize = 10.sp, color = TextDim, fontWeight = FontWeight.Bold)
                                    Text(node.type, color = CyberCyan, fontWeight = FontWeight.Black, fontSize = 15.sp)
                                }
                                Column(modifier = Modifier.weight(1f)) {
                                    Text("MONTHLY AMORTIZATION", fontSize = 10.sp, color = TextDim, fontWeight = FontWeight.Bold)
                                    Text(
                                        text = if (node.costEstimate > 0) "$${String.format(Locale.US, "%,.2f", node.costEstimate)}" else "Free/Tier",
                                        color = TextWhite,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 15.sp
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.height(12.dp))

                            Text("INFRASTRUCTURE DISCOVERED BLUEPRINT", fontSize = 10.sp, color = TextDim, fontWeight = FontWeight.Bold)
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = node.configurationHint,
                                color = TextWhite,
                                fontSize = 13.sp,
                                fontFamily = FontFamily.Monospace,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(DeepCard)
                                    .padding(8.dp)
                                    .border(1.dp, BorderGrey, RoundedCornerShape(4.dp))
                            )

                            // Audit Risk alert if AWS EC2 / S3
                            if (node.type == "EC2" || node.type == "S3") {
                                Spacer(modifier = Modifier.height(12.dp))
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .background(WarningAmber.copy(alpha = 0.15f))
                                        .border(1.dp, WarningAmber, RoundedCornerShape(4.dp))
                                        .padding(8.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.Security,
                                        contentDescription = "Risk warning",
                                        tint = WarningAmber,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = if (node.type == "EC2") "VULNERABILITY: Public port 22 SSH open with 0.0.0.0/0 wildcard!"
                                        else "RISK: Unencrypted S3 payload detected. KMS secure transfer required.",
                                        color = WarningAmber,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                }
                            }

                            // Trigger actions links to Terraform Generator
                            Spacer(modifier = Modifier.height(16.dp))
                            Button(
                                onClick = {
                                    viewModel.selectGraphNode(null)
                                    onNavigateToGenerator()
                                },
                                shape = RoundedCornerShape(6.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = ElectricBlue),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .testTag("action_migrate_button")
                            ) {
                                Icon(Icons.Default.DriveFileMove, contentDescription = "Migration target icon")
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Generate Migration Path to Azure")
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun GraphNodeItem(
    resource: DiscoveryResource?,
    x: Int,
    y: Int,
    isSelected: Boolean,
    onClick: (DiscoveryResource) -> Unit
) {
    if (resource == null) return

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

    val themeColor = when (resource.type) {
        "EC2" -> AWSColor
        "RDS" -> ElectricBlue
        "S3" -> WarningAmber
        "Lambda" -> NebulaPurple
        else -> CyberCyan
    }

    // Centering offsets
    val nodeWidth = 120.dp
    val nodeHeight = 84.dp

    Box(
        modifier = Modifier
            .offset { IntOffset((x.dp.toPx() - (nodeWidth.toPx() / 2)).toInt(), (y.dp.toPx() - (nodeHeight.toPx() / 2)).toInt()) }
            .size(width = nodeWidth, height = nodeHeight)
            .clip(RoundedCornerShape(8.dp))
            .background(DeepCard)
            .border(
                width = if (isSelected) 2.dp else 1.dp,
                color = if (isSelected) CyberCyan else BorderGrey,
                shape = RoundedCornerShape(8.dp)
            )
            .clickable { onClick(resource) }
            .padding(6.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween,
            modifier = Modifier.fillMaxSize()
        ) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .clip(CircleShape)
                    .background(themeColor.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = themeColor,
                    modifier = Modifier.size(14.dp)
                )
            }
            Text(
                text = resource.name,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = TextWhite,
                textAlign = TextAlign.Center,
                maxLines = 1
            )
            Text(
                text = resource.type,
                fontSize = 8.sp,
                fontFamily = FontFamily.Monospace,
                color = TextDim,
                fontWeight = FontWeight.Medium
            )
        }
    }
}
