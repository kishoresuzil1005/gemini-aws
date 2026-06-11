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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.CloudViewModel
import com.example.ui.theme.*
import java.util.Locale

@Composable
fun DependencyGraphScreen(
    viewModel: CloudViewModel,
    onNavigateToGenerator: () -> Unit,
    modifier: Modifier = Modifier
) {
    val level1 by viewModel.topologyLevel1.collectAsState()
    val level2 by viewModel.topologyLevel2.collectAsState()
    val level3 by viewModel.topologyLevel3.collectAsState()
    
    val currentCategory by viewModel.currentTopologyCategory.collectAsState()
    val currentId by viewModel.currentTopologyResourceId.collectAsState()

    val hasData = (level1 != null && level1!!.nodes.isNotEmpty())

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
                    modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    if (currentCategory != null || currentId != null) {
                        IconButton(onClick = { viewModel.clearTopologySelection() }) {
                            Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberCyan)
                        }
                    }
                    val title = if (currentId != null) "Resource: $currentId"
                                else if (currentCategory != null) "Category: ${currentCategory?.capitalize()}"
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
                    targetState = Triple(currentCategory, currentId, level1),
                    label = "Topology Transition"
                ) { state ->
                    val (cat, id, l1) = state
                    if (id != null && level3 != null) {
                        // LEVEL 3
                        LazyColumn(modifier = Modifier.fillMaxSize()) {
                            item {
                                Text("Dependencies", fontSize = 12.sp, color = TextDim, modifier = Modifier.padding(bottom = 8.dp))
                            }
                            items(level3!!.dependencies) { dep ->
                                Card(
                                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                    colors = CardDefaults.cardColors(containerColor = DeepCard)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(16.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(Icons.Default.Link, contentDescription = null, tint = CyberCyan)
                                        Spacer(modifier = Modifier.width(16.dp))
                                        Column {
                                            Text(dep.name, color = TextWhite, fontWeight = FontWeight.Bold)
                                            Text(dep.type, color = TextDim, fontSize = 12.sp)
                                        }
                                    }
                                }
                            }
                        }
                    } else if (cat != null && level2 != null) {
                        // LEVEL 2
                        LazyColumn(modifier = Modifier.fillMaxSize()) {
                            items(level2!!.nodes) { node ->
                                Card(
                                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                                        .clickable { viewModel.loadTopologyResource(node.id) },
                                    colors = CardDefaults.cardColors(containerColor = DeepCard)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(16.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(Icons.Default.List, contentDescription = null, tint = ElectricBlue)
                                        Spacer(modifier = Modifier.width(16.dp))
                                        Column {
                                            Text(node.name, color = TextWhite, fontWeight = FontWeight.Bold)
                                            Text("Type: ${node.type}", color = TextDim, fontSize = 12.sp)
                                        }
                                        Spacer(modifier = Modifier.weight(1f))
                                        Icon(Icons.Default.ChevronRight, contentDescription = "Drill down", tint = TextDim)
                                    }
                                }
                            }
                        }
                    } else if (l1 != null) {
                        // LEVEL 1
                        LazyColumn(modifier = Modifier.fillMaxSize()) {
                            items(l1.nodes) { node ->
                                Card(
                                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
                                        .clickable { viewModel.loadTopologyCategory(node.id) },
                                    colors = CardDefaults.cardColors(containerColor = DeepCard)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(16.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(Icons.Default.Folder, contentDescription = null, tint = WarningAmber)
                                        Spacer(modifier = Modifier.width(16.dp))
                                        Column {
                                            Text(node.name, color = TextWhite, fontWeight = FontWeight.Bold)
                                            Text("Resources: ${node.count}", color = TextDim, fontSize = 12.sp)
                                        }
                                        Spacer(modifier = Modifier.weight(1f))
                                        Icon(Icons.Default.ChevronRight, contentDescription = "Drill down", tint = TextDim)
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
