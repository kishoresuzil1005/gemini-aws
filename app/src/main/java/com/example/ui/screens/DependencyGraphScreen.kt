package com.example.ui.screens

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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import com.example.api.GraphResourceNode
import com.example.api.GraphResponse
import com.example.api.GraphNode
import com.example.ui.CloudViewModel
import com.example.ui.theme.*
import java.util.Locale

@Composable
fun DependencyGraphScreen(
    viewModel: CloudViewModel,
    onNavigateToGenerator: () -> Unit,
    modifier: Modifier = Modifier
) {
    val categories by viewModel.topologyCategories.collectAsState()
    val level2Resources by viewModel.topologyResources.collectAsState()
    val level3 by viewModel.topologyLevel3.collectAsState()
    val resourceGraph by viewModel.resourceGraph.collectAsState()
    
    val currentCategory by viewModel.currentTopologyCategory.collectAsState()
    val currentId by viewModel.currentTopologyResourceId.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.refreshAllFeeds()
    }

    val hasData = categories.isNotEmpty()

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(SpaceSlate)
            .testTag("dependency_graph_screen")
    ) {
        if (!hasData) {
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
                    text = "Initiate a Cloud Discovery Scan in the Dashboard console first to populate dependencies.",
                    color = TextDim,
                    fontSize = 14.sp,
                    textAlign = TextAlign.Center
                )
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
            ) {
                // Header with back button if drilled down
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    if (currentCategory != null || currentId != null) {
                        IconButton(
                            onClick = { viewModel.clearTopologySelection() },
                            modifier = Modifier
                                .padding(end = 8.dp)
                                .background(DeepCard, CircleShape)
                                .border(1.dp, BorderGrey, CircleShape)
                        ) {
                            Icon(
                                imageVector = Icons.Default.ArrowBack,
                                contentDescription = "Back",
                                tint = CyberCyan,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                    }
                    val title = if (currentId != null) "Resource Dependencies"
                                else if (currentCategory != null) "Category: ${currentCategory?.replaceFirstChar { it.uppercase() }}"
                                else "AWS Account Resources"
                    Text(
                        text = title,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextWhite
                    )
                }
                
                // Content Switcher
                AnimatedContent(
                    targetState = Triple(currentCategory, currentId, categories),
                    label = "Topology Transition",
                    modifier = Modifier.weight(1f)
                ) { state ->
                    val (cat, id, cats) = state
                    if (id != null && level3 != null) {
                        // LEVEL 3 - Dependencies details
                        val currentResName = level3!!.resource.name
                        val currentResId = level3!!.resource.id
                        val currentResType = remember(currentResId, currentCategory) {
                            guessResourceType(currentResId, currentCategory)
                        }
                        
                        Column(
                            modifier = Modifier
                                .fillMaxSize()
                                .verticalScroll(rememberScrollState())
                        ) {
                            // Selected source resource card
                            Card(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(bottom = 16.dp),
                                colors = CardDefaults.cardColors(containerColor = DeepCard),
                                border = BorderStroke(1.5.dp, CyberCyan.copy(alpha = 0.8f))
                            ) {
                                Row(
                                    modifier = Modifier.padding(16.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(44.dp)
                                            .background(CyberCyan.copy(alpha = 0.15f), CircleShape)
                                            .border(1.dp, CyberCyan.copy(alpha = 0.4f), CircleShape),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Icon(
                                            imageVector = getResourceIcon(currentResType),
                                            contentDescription = null,
                                            tint = CyberCyan,
                                            modifier = Modifier.size(24.dp)
                                        )
                                    }
                                    Spacer(modifier = Modifier.width(16.dp))
                                    Column {
                                        Text(
                                            text = currentResName,
                                            color = TextWhite,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 18.sp
                                        )
                                        Text(
                                            text = "ID: $currentResId",
                                            color = TextDim,
                                            fontSize = 12.sp,
                                            fontFamily = FontFamily.Monospace
                                        )
                                        Text(
                                            text = "PROVIDER: AWS | COGNITIVE CLASSIFICATION: $currentResType",
                                            color = CyberCyan,
                                            fontSize = 10.sp,
                                            fontFamily = FontFamily.Monospace,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }
                                }
                            }

                            // --- REAL RELATIONSHIP TOPOLOGY GRAPH ---
                            Text(
                                text = "REAL-TIME TOPOLOGY GRAPH NETWORKMAP",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = TextDim,
                                modifier = Modifier.padding(bottom = 8.dp)
                            )

                            Card(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(bottom = 16.dp),
                                colors = CardDefaults.cardColors(containerColor = DeepCard),
                                border = BorderStroke(1.dp, BorderGrey)
                            ) {
                                Column(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(16.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    // 1. Upstream Reliant Resources
                                    val inboundNodes = remember(resourceGraph, currentResId) {
                                        resourceGraph?.nodes?.filter { n ->
                                            n.id != currentResId && resourceGraph?.edges?.any { e -> e.source == n.id && e.target == currentResId } == true
                                        } ?: emptyList()
                                    }

                                    if (inboundNodes.isNotEmpty()) {
                                        Text(
                                            text = "UPSTREAM RELIANT RESOURCES",
                                            fontSize = 10.sp,
                                            fontFamily = FontFamily.Monospace,
                                            fontWeight = FontWeight.Bold,
                                            color = ElectricBlue,
                                            modifier = Modifier.padding(bottom = 6.dp)
                                        )

                                        Row(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .horizontalScroll(rememberScrollState())
                                                .padding(bottom = 8.dp),
                                            horizontalArrangement = Arrangement.Center
                                        ) {
                                            inboundNodes.forEach { node ->
                                                Card(
                                                    colors = CardDefaults.cardColors(containerColor = SpaceSlate),
                                                    border = BorderStroke(1.dp, ElectricBlue.copy(alpha = 0.4f)),
                                                    modifier = Modifier.padding(horizontal = 4.dp)
                                                ) {
                                                    Row(
                                                        modifier = Modifier.padding(8.dp),
                                                        verticalAlignment = Alignment.CenterVertically
                                                    ) {
                                                        Icon(
                                                            imageVector = getResourceIcon(node.type),
                                                            contentDescription = null,
                                                            tint = ElectricBlue,
                                                            modifier = Modifier.size(12.dp)
                                                        )
                                                        Spacer(modifier = Modifier.width(6.dp))
                                                        Text(
                                                            text = node.name,
                                                            fontSize = 11.sp,
                                                            color = TextWhite,
                                                            fontWeight = FontWeight.Bold
                                                        )
                                                    }
                                                }
                                            }
                                        }

                                        Icon(
                                            imageVector = Icons.Default.ArrowDownward,
                                            contentDescription = null,
                                            tint = ElectricBlue.copy(alpha = 0.6f),
                                            modifier = Modifier
                                                .size(20.dp)
                                                .padding(bottom = 8.dp)
                                        )
                                    }

                                    // 2. Focused Core Resource Card (Middle)
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(CyberCyan.copy(alpha = 0.1f))
                                            .border(1.5.dp, CyberCyan, RoundedCornerShape(8.dp))
                                            .padding(horizontal = 16.dp, vertical = 10.dp),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Icon(
                                                imageVector = getResourceIcon(currentResType),
                                                contentDescription = null,
                                                tint = CyberCyan,
                                                modifier = Modifier.size(16.dp)
                                            )
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text(
                                                text = currentResId,
                                                fontSize = 13.sp,
                                                fontWeight = FontWeight.ExtraBold,
                                                color = TextWhite,
                                                fontFamily = FontFamily.Monospace
                                            )
                                        }
                                    }

                                    // 3. Downstream Dependencies (Connections outbound)
                                    val outboundNodes = remember(resourceGraph, currentResId) {
                                        resourceGraph?.nodes?.filter { n ->
                                            n.id != currentResId && resourceGraph?.edges?.any { e -> e.source == currentResId && e.target == n.id } == true
                                        } ?: emptyList()
                                    }

                                    val finalOutbounds = if (outboundNodes.isEmpty()) {
                                        level3!!.dependencies.map { dep ->
                                            GraphResourceNode(id = dep.name, type = dep.type, name = dep.name)
                                        }
                                    } else {
                                        outboundNodes
                                    }

                                    if (finalOutbounds.isNotEmpty()) {
                                        Icon(
                                            imageVector = Icons.Default.ArrowDownward,
                                            contentDescription = null,
                                            tint = NebulaPurple.copy(alpha = 0.6f),
                                            modifier = Modifier
                                                .size(20.dp)
                                                .padding(vertical = 4.dp)
                                        )

                                        Text(
                                            text = "DOWNSTREAM TARGET DEPENDENCIES",
                                            fontSize = 10.sp,
                                            fontFamily = FontFamily.Monospace,
                                            fontWeight = FontWeight.Bold,
                                            color = NebulaPurple,
                                            modifier = Modifier.padding(bottom = 6.dp)
                                        )

                                        Row(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .horizontalScroll(rememberScrollState()),
                                            horizontalArrangement = Arrangement.Center
                                        ) {
                                            finalOutbounds.forEach { node ->
                                                Card(
                                                    colors = CardDefaults.cardColors(containerColor = SpaceSlate),
                                                    border = BorderStroke(1.dp, NebulaPurple.copy(alpha = 0.4f)),
                                                    modifier = Modifier.padding(horizontal = 4.dp)
                                                ) {
                                                    Row(
                                                        modifier = Modifier.padding(8.dp),
                                                        verticalAlignment = Alignment.CenterVertically
                                                    ) {
                                                        Icon(
                                                            imageVector = getResourceIcon(node.type),
                                                            contentDescription = null,
                                                            tint = NebulaPurple,
                                                            modifier = Modifier.size(12.dp)
                                                        )
                                                        Spacer(modifier = Modifier.width(6.dp))
                                                        Text(
                                                            text = node.name,
                                                            fontSize = 11.sp,
                                                            color = TextWhite,
                                                            fontWeight = FontWeight.Bold
                                                        )
                                                    }
                                                }
                                            }
                                        }
                                    } else {
                                        Spacer(modifier = Modifier.height(8.dp))
                                        Text(
                                            text = "No outbound dependencies map definitions.",
                                            fontSize = 11.sp,
                                            color = TextDim
                                        )
                                    }
                                }
                            }

                            // --- SECTION: ENTERPRISE DISRUPTION ANALYSIS ---
                            Text(
                                text = "ENTERPRISE DISRUPTION & COUPLING ASSESSMENT",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = TextDim,
                                modifier = Modifier.padding(bottom = 8.dp)
                            )

                            val impacts = resourceGraph?.impact_analysis ?: emptyList()
                            if (impacts.isEmpty()) {
                                Card(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(bottom = 16.dp),
                                    colors = CardDefaults.cardColors(containerColor = DeepCard),
                                    border = BorderStroke(1.dp, BorderGrey)
                                ) {
                                    Column(
                                        modifier = Modifier.padding(24.dp),
                                        horizontalAlignment = Alignment.CenterHorizontally
                                    ) {
                                        Icon(
                                            imageVector = Icons.Default.Shield,
                                            contentDescription = "Safe Deletion Profile",
                                            tint = TerminalGreen,
                                            modifier = Modifier.size(36.dp)
                                        )
                                        Spacer(modifier = Modifier.height(12.dp))
                                        Text(
                                            text = "Isolated Topology Signature",
                                            color = TextWhite,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 14.sp
                                        )
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Text(
                                            text = "Tearing down this node is deemed a safe operations procedure with zero upstream service coupling risks identified.",
                                            color = TextDim,
                                            fontSize = 12.sp,
                                            textAlign = TextAlign.Center
                                        )
                                    }
                                }
                            } else {
                                impacts.forEach { imp ->
                                    val isCritical = imp.impact.contains("CRITICAL") || imp.impact.contains("RISK") || imp.impact.contains("loss") || imp.impact.contains("OUTAGE")
                                    val riskColor = if (isCritical) BentoAccentRed else WarningAmber
                                    val riskLabel = if (isCritical) "CRITICAL RISK PROFILE" else "SERVICE RISK CONSTRAINT"

                                    Card(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 8.dp),
                                        colors = CardDefaults.cardColors(containerColor = DeepCard),
                                        border = BorderStroke(1.dp, riskColor.copy(alpha = 0.4f))
                                    ) {
                                        Column(modifier = Modifier.padding(14.dp)) {
                                            Row(
                                                modifier = Modifier.fillMaxWidth(),
                                                verticalAlignment = Alignment.CenterVertically
                                            ) {
                                                Box(
                                                    modifier = Modifier
                                                        .size(32.dp)
                                                        .background(riskColor.copy(alpha = 0.12f), CircleShape),
                                                    contentAlignment = Alignment.Center
                                                ) {
                                                    Icon(
                                                        imageVector = getResourceIcon(imp.type),
                                                        contentDescription = null,
                                                        tint = riskColor,
                                                        modifier = Modifier.size(16.dp)
                                                    )
                                                }
                                                Spacer(modifier = Modifier.width(12.dp))
                                                Column(modifier = Modifier.weight(1f)) {
                                                    Text(
                                                        text = imp.name,
                                                        color = TextWhite,
                                                        fontWeight = FontWeight.Bold,
                                                        fontSize = 13.sp
                                                    )
                                                    Text(
                                                        text = "TYPE: ${imp.type.uppercase(Locale.US)}",
                                                        color = TextDim,
                                                        fontSize = 10.sp,
                                                        fontFamily = FontFamily.Monospace
                                                    )
                                                }
                                                Box(
                                                    modifier = Modifier
                                                        .clip(RoundedCornerShape(4.dp))
                                                        .background(riskColor.copy(alpha = 0.12f))
                                                        .padding(horizontal = 6.dp, vertical = 3.dp)
                                                ) {
                                                    Text(
                                                        text = riskLabel,
                                                        color = riskColor,
                                                        fontSize = 8.sp,
                                                        fontWeight = FontWeight.Bold,
                                                        fontFamily = FontFamily.Monospace
                                                    )
                                                }
                                            }
                                            Spacer(modifier = Modifier.height(10.dp))
                                            Text(
                                                text = imp.impact,
                                                color = TextWhite.copy(alpha = 0.85f),
                                                fontSize = 12.sp,
                                                lineHeight = 16.sp,
                                                fontWeight = FontWeight.Medium
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    } else if (cat != null) {
                        // LEVEL 2 - Grouped resources by category
                        if (level2Resources.isEmpty()) {
                            Box(
                                modifier = Modifier.fillMaxSize(),
                                contentAlignment = Alignment.Center
                            ) {
                                CircularProgressIndicator(color = CyberCyan)
                            }
                        } else {
                            val groupedTypeResources = remember(level2Resources) {
                                level2Resources.groupBy { it.type }
                            }
                            
                            LazyColumn(modifier = Modifier.fillMaxSize()) {
                                groupedTypeResources.forEach { (type, typeResources) ->
                                    item {
                                        Row(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .padding(top = 16.dp, bottom = 8.dp),
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Box(
                                                modifier = Modifier
                                                    .size(24.dp)
                                                    .background(NebulaPurple.copy(alpha = 0.15f), RoundedCornerShape(4.dp)),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Icon(
                                                    imageVector = getResourceIcon(type),
                                                    contentDescription = null,
                                                    tint = NebulaPurple,
                                                    modifier = Modifier.size(14.dp)
                                                )
                                            }
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text(
                                                text = "$type (${typeResources.size})",
                                                color = CyberCyan,
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 15.sp,
                                                fontFamily = FontFamily.Monospace
                                            )
                                        }
                                    }
                                    
                                    items(typeResources) { resource ->
                                        Card(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .padding(vertical = 4.dp)
                                                .clickable { viewModel.loadTopologyResource(resource.id) },
                                            colors = CardDefaults.cardColors(containerColor = DeepCard),
                                            border = BorderStroke(1.dp, BorderGrey)
                                        ) {
                                            Row(
                                                modifier = Modifier.padding(16.dp),
                                                verticalAlignment = Alignment.CenterVertically
                                            ) {
                                                Column(modifier = Modifier.weight(1f)) {
                                                    Text(
                                                        text = resource.name,
                                                        color = TextWhite,
                                                        fontWeight = FontWeight.Bold,
                                                        fontSize = 14.sp
                                                    )
                                                    Spacer(modifier = Modifier.height(2.dp))
                                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                                        Icon(
                                                            imageVector = Icons.Default.Place,
                                                            contentDescription = null,
                                                            tint = TextDim,
                                                            modifier = Modifier.size(12.dp)
                                                        )
                                                        Spacer(modifier = Modifier.width(4.dp))
                                                        Text(
                                                            text = resource.region,
                                                            color = TextDim,
                                                            fontSize = 12.sp
                                                        )
                                                    }
                                                }
                                                
                                                StatusBadge(status = resource.status)
                                                Spacer(modifier = Modifier.width(12.dp))
                                                Icon(
                                                    imageVector = Icons.Default.ChevronRight,
                                                    contentDescription = "Drill down to connections",
                                                    tint = TextDim,
                                                    modifier = Modifier.size(16.dp)
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    } else {
                        // LEVEL 1 - View selection: Interactive Network Map or Classified List
                        var currentViewMode by remember { mutableStateOf("NETWORK") }
                        
                        Column(modifier = Modifier.fillMaxSize()) {
                            TabRow(
                                selectedTabIndex = if (currentViewMode == "NETWORK") 0 else 1,
                                containerColor = SpaceSlate,
                                contentColor = CyberCyan,
                                indicator = { tabPositions ->
                                    TabRowDefaults.SecondaryIndicator(
                                        modifier = Modifier.tabIndicatorOffset(tabPositions[if (currentViewMode == "NETWORK") 0 else 1]),
                                        color = CyberCyan
                                    )
                                },
                                modifier = Modifier.padding(bottom = 12.dp)
                            ) {
                                Tab(
                                    selected = currentViewMode == "NETWORK",
                                    onClick = { currentViewMode = "NETWORK" },
                                    text = { 
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Icon(Icons.Default.Hub, contentDescription = null, modifier = Modifier.size(16.dp))
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text("NETWORK MAP", fontWeight = FontWeight.Bold, fontSize = 13.sp)
                                        }
                                    }
                                )
                                Tab(
                                    selected = currentViewMode == "LIST",
                                    onClick = { currentViewMode = "LIST" },
                                    text = {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Icon(Icons.Default.List, contentDescription = null, modifier = Modifier.size(16.dp))
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text("LIST CLASSIFIED", fontWeight = FontWeight.Bold, fontSize = 13.sp)
                                        }
                                    }
                                )
                            }
                            
                            if (currentViewMode == "NETWORK") {
                                val graphTopology by viewModel.graphTopology.collectAsState()
                                val graph = graphTopology
                                if (graph == null || graph.nodes.isEmpty()) {
                                    Box(
                                        modifier = Modifier.fillMaxSize(),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                            CircularProgressIndicator(color = CyberCyan)
                                            Spacer(modifier = Modifier.height(12.dp))
                                            Text("Querying Neo4j Graph Topology...", color = TextDim, fontSize = 12.sp)
                                        }
                                    }
                                } else {
                                    RealTopologyNetworkMap(graph = graph) { selectedNodeId ->
                                        viewModel.loadTopologyResource(selectedNodeId)
                                    }
                                }
                            } else {
                                LazyColumn(modifier = Modifier.fillMaxSize()) {
                                    items(cats) { node ->
                                        val categoryIcon = getCategoryIcon(node.name)
                                        val categoryColor = getCategoryColor(node.name)
                                        Card(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .padding(vertical = 6.dp)
                                                .clickable { viewModel.loadTopologyCategory(node.name) },
                                            colors = CardDefaults.cardColors(containerColor = DeepCard),
                                            border = BorderStroke(1.dp, BorderGrey)
                                        ) {
                                            Row(
                                                modifier = Modifier.padding(16.dp),
                                                verticalAlignment = Alignment.CenterVertically
                                            ) {
                                                Box(
                                                    modifier = Modifier
                                                        .size(44.dp)
                                                        .background(categoryColor.copy(alpha = 0.1f), CircleShape)
                                                        .border(1.dp, categoryColor.copy(alpha = 0.3f), CircleShape),
                                                    contentAlignment = Alignment.Center
                                                ) {
                                                    Icon(
                                                        imageVector = categoryIcon,
                                                        contentDescription = null,
                                                        tint = categoryColor,
                                                        modifier = Modifier.size(20.dp)
                                                    )
                                                }
                                                Spacer(modifier = Modifier.width(16.dp))
                                                Column(modifier = Modifier.weight(1f)) {
                                                    Text(
                                                        text = node.name,
                                                        color = TextWhite,
                                                        fontWeight = FontWeight.Bold,
                                                        fontSize = 16.sp
                                                    )
                                                    Text(
                                                        text = "Active inventory resources",
                                                        color = TextDim,
                                                        fontSize = 12.sp
                                                    )
                                                }
                                                Row(
                                                    verticalAlignment = Alignment.CenterVertically,
                                                    horizontalArrangement = Arrangement.End
                                                ) {
                                                    Box(
                                                        modifier = Modifier
                                                            .clip(RoundedCornerShape(6.dp))
                                                            .background(categoryColor.copy(alpha = 0.15f))
                                                            .padding(horizontal = 8.dp, vertical = 4.dp)
                                                    ) {
                                                        Text(
                                                            text = node.count.toString(),
                                                            color = categoryColor,
                                                            fontWeight = FontWeight.ExtraBold,
                                                            fontSize = 13.sp
                                                        )
                                                    }
                                                    Spacer(modifier = Modifier.width(12.dp))
                                                    Icon(
                                                        imageVector = Icons.Default.ChevronRight,
                                                        contentDescription = "Open Category",
                                                        tint = TextDim,
                                                        modifier = Modifier.size(18.dp)
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun StatusBadge(status: String) {
    val isGood = status.lowercase(Locale.US) in listOf("running", "active", "available", "on")
    val badgeColor = if (isGood) TerminalGreen else WarningAmber
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(4.dp))
            .background(badgeColor.copy(alpha = 0.12f))
            .border(1.dp, badgeColor.copy(alpha = 0.4f), RoundedCornerShape(4.dp))
            .padding(horizontal = 8.dp, vertical = 2.dp)
    ) {
        Text(
            text = status.uppercase(Locale.US),
            color = badgeColor,
            fontSize = 9.sp,
            fontWeight = FontWeight.Bold,
            fontFamily = FontFamily.Monospace,
            letterSpacing = 0.5.sp
        )
    }
}

fun getResourceIcon(type: String): ImageVector {
    return when (type.uppercase(Locale.US)) {
        "EC2" -> Icons.Default.Memory
        "LAMBDA" -> Icons.Default.FlashOn
        "S3" -> Icons.Default.Layers
        "EBS" -> Icons.Default.Storage
        "RDS" -> Icons.Default.Storage
        "VPC" -> Icons.Default.Cloud
        "ALB" -> Icons.Default.AltRoute
        "IAM" -> Icons.Default.Lock
        "SECURITYGROUP" -> Icons.Default.Shield
        "SUBNET" -> Icons.Default.Splitscreen
        else -> Icons.Default.Dns
    }
}

fun getCategoryIcon(name: String): ImageVector {
    return when (name.lowercase(Locale.US)) {
        "compute" -> Icons.Default.Memory
        "storage" -> Icons.Default.Layers
        "database" -> Icons.Default.Storage
        "network" -> Icons.Default.Cloud
        "security" -> Icons.Default.Shield
        else -> Icons.Default.Folder
    }
}

fun getCategoryColor(name: String): Color {
    return when (name.lowercase(Locale.US)) {
        "compute" -> AWSColor
        "storage" -> NebulaPurple
        "database" -> WarningAmber
        "network" -> CyberCyan
        "security" -> ElectricBlue
        else -> TextDim
    }
}

fun guessResourceType(resourceId: String, category: String?): String {
    val id = resourceId.lowercase(Locale.US)
    return when {
        id.startsWith("i-") -> "EC2"
        id.startsWith("vpc-") -> "VPC"
        id.startsWith("subnet-") -> "SUBNET"
        id.startsWith("sg-") -> "SECURITYGROUP"
        id.startsWith("vol-") -> "EBS"
        id.startsWith("db-") -> "RDS"
        category?.lowercase(Locale.US) == "compute" -> "EC2"
        category?.lowercase(Locale.US) == "database" -> "RDS"
        category?.lowercase(Locale.US) == "storage" -> "S3"
        category?.lowercase(Locale.US) == "network" -> "VPC"
        category?.lowercase(Locale.US) == "security" -> "IAM"
        else -> "RESOURCE"
    }
}

@Composable
fun RealTopologyNetworkMap(
    graph: GraphResponse,
    onNodeSelect: (String) -> Unit
) {
    val vpcNodes = remember(graph) { graph.nodes.filter { it.type.uppercase(Locale.US) == "VPC" } }
    val networkNodes = remember(graph) { graph.nodes.filter { it.type.uppercase(Locale.US) in listOf("SUBNET", "ALB") } }
    val computeNodes = remember(graph) { graph.nodes.filter { it.type.uppercase(Locale.US) in listOf("EC2", "LAMBDA") } }
    val storageNodes = remember(graph) { graph.nodes.filter { it.type.uppercase(Locale.US) in listOf("RDS", "EBS", "S3") } }
    val otherNodes = remember(graph) { 
        graph.nodes.filter { 
            it.type.uppercase(Locale.US) !in listOf("VPC", "SUBNET", "ALB", "EC2", "LAMBDA", "RDS", "EBS", "S3") 
        } 
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(bottom = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            colors = CardDefaults.cardColors(containerColor = SpaceSlate),
            border = BorderStroke(1.dp, CyberCyan.copy(alpha = 0.2f))
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                Text(
                    text = "NEO4J RECONSTRUCTED MODEL",
                    fontSize = 11.sp,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    color = CyberCyan
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Explore the actual node connectivities and parent-child bindings. Click any node card below to perform deep blast-radius and coupling assessments.",
                    fontSize = 12.sp,
                    color = TextDim,
                    lineHeight = 16.sp
                )
            }
        }

        // Tier 1: Networks
        if (vpcNodes.isNotEmpty()) {
            Text(
                text = "NETWORK & SECURITY INGRESS",
                fontSize = 10.sp,
                fontFamily = FontFamily.Monospace,
                color = CyberCyan,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 4.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                vpcNodes.forEach { node ->
                    NetworkNodeCard(node = node, onClick = { onNodeSelect(node.id) })
                }
            }
            
            VerticalConnectorLine()
        }

        // Tier 1.5: Subnets & ALBs
        if (networkNodes.isNotEmpty()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 4.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                networkNodes.forEach { node ->
                    NetworkNodeCard(node = node, onClick = { onNodeSelect(node.id) })
                }
            }
            
            VerticalConnectorLine()
        }

        // Tier 2: Compute
        if (computeNodes.isNotEmpty()) {
            Text(
                text = "COMPUTE WORKLOAD INSTANCES",
                fontSize = 10.sp,
                fontFamily = FontFamily.Monospace,
                color = AWSColor,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 4.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                computeNodes.forEach { node ->
                    NetworkNodeCard(node = node, onClick = { onNodeSelect(node.id) })
                }
            }
            
            VerticalConnectorLine()
        }

        // Tier 3: Storage & DB
        if (storageNodes.isNotEmpty()) {
            Text(
                text = "DATABASES & PERSISTENT STORAGE",
                fontSize = 10.sp,
                fontFamily = FontFamily.Monospace,
                color = NebulaPurple,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 4.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                storageNodes.forEach { node ->
                    NetworkNodeCard(node = node, onClick = { onNodeSelect(node.id) })
                }
            }
        }

        // Tier 4: Other / Unclassified
        if (otherNodes.isNotEmpty()) {
            VerticalConnectorLine()
            Text(
                text = "CLOUD SECURITY & METADATA",
                fontSize = 10.sp,
                fontFamily = FontFamily.Monospace,
                color = TextDim,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState())
                    .padding(horizontal = 4.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                otherNodes.forEach { node ->
                    NetworkNodeCard(node = node, onClick = { onNodeSelect(node.id) })
                }
            }
        }
    }
}

@Composable
fun NetworkNodeCard(
    node: GraphNode,
    onClick: () -> Unit
) {
    val nodeColor = when (node.type.uppercase(Locale.US)) {
        "VPC", "SUBNET" -> CyberCyan
        "ALB" -> ElectricBlue
        "EC2", "LAMBDA" -> AWSColor
        "RDS", "S3" -> WarningAmber
        "EBS" -> NebulaPurple
        else -> TextDim
    }

    Card(
        modifier = Modifier
            .padding(4.dp)
            .width(135.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = DeepCard),
        border = BorderStroke(1.2.dp, nodeColor.copy(alpha = 0.6f))
    ) {
        Column(
            modifier = Modifier.padding(10.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .background(nodeColor.copy(alpha = 0.12f), CircleShape)
                    .border(1.dp, nodeColor.copy(alpha = 0.3f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = getResourceIcon(node.type),
                    contentDescription = null,
                    tint = nodeColor,
                    modifier = Modifier.size(16.dp)
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = node.type,
                fontSize = 9.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                color = nodeColor,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = node.name,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = TextWhite,
                maxLines = 1,
                textAlign = TextAlign.Center
            )
            Text(
                text = node.id,
                fontSize = 8.sp,
                fontFamily = FontFamily.Monospace,
                color = TextDim,
                maxLines = 1,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
fun VerticalConnectorLine() {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .fillMaxWidth()
            .height(24.dp)
    ) {
        Box(
            modifier = Modifier
                .width(2.dp)
                .fillMaxHeight()
                .background(BorderGrey.copy(alpha = 0.6f))
        )
    }
}
