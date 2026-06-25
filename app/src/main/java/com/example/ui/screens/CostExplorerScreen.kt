package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.CloudViewModel
import java.text.SimpleDateFormat
import java.util.*

val AwsBlue = Color(0xFF0073BB)
val AwsOrange = Color(0xFFFF9900)
val AwsGreen = Color(0xFF1D8102)
val AwsPurple = Color(0xFF6B5B95)
val AwsRed = Color(0xFFD13212)
val ThemeDarkBg = Color(0xFF0F0E13)
val ThemeLightBg = Color(0xFFF2F3F3)
val CardDarkBg = Color(0xFF151419)
val CardLightBg = Color.White
val BorderDark = Color(0xFF2C2A35)
val BorderLight = Color(0xFFEAEAED)
val TextDarkPrimary = Color(0xFFF1F1F1)
val TextDarkSecondary = Color(0xFF9E9BA8)
val TextLightPrimary = Color(0xFF16191F)
val TextLightSecondary = Color(0xFF545B64)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CostExplorerScreen(
    viewModel: CloudViewModel,
    isDarkTheme: Boolean,
    onBack: () -> Unit
) {
    val bgColor = if (isDarkTheme) ThemeDarkBg else ThemeLightBg
    val cardBg = if (isDarkTheme) CardDarkBg else CardLightBg
    val borderColor = if (isDarkTheme) BorderDark else BorderLight
    val textPrimary = if (isDarkTheme) TextDarkPrimary else TextLightPrimary
    val textSecondary = if (isDarkTheme) TextDarkSecondary else TextLightSecondary

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(bgColor)
    ) {
        // App Bar
        TopAppBar(
            title = {
                Text("Cost Explorer", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textPrimary)
            },
            navigationIcon = {
                IconButton(onClick = onBack) {
                    Icon(imageVector = Icons.Default.ArrowBack, contentDescription = "Back", tint = textPrimary)
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = cardBg
            ),
            actions = {
                OutlinedButton(
                    onClick = { /* Save report */ },
                    border = borderStroke(borderColor),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = textPrimary),
                    modifier = Modifier.padding(end = 8.dp)
                ) {
                    Text("Save to report library")
                }
            }
        )
        HorizontalDivider(color = borderColor)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Filters section
            Card(
                colors = CardDefaults.cardColors(containerColor = cardBg),
                border = BorderStroke(1.dp, borderColor),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Report parameters", fontWeight = FontWeight.Bold, color = textPrimary, fontSize = 16.sp)
                    Spacer(modifier = Modifier.height(12.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        DropdownFilterButton("Date range", "Last 30 Days", isDarkTheme)
                        DropdownFilterButton("Granularity", "Daily", isDarkTheme)
                        DropdownFilterButton("Group by", "Service", isDarkTheme)
                    }
                }
            }

            // Chart section
            Card(
                colors = CardDefaults.cardColors(containerColor = cardBg),
                border = BorderStroke(1.dp, borderColor),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Total costs", color = textSecondary, fontSize = 12.sp)
                            Text("$2,456.89", fontWeight = FontWeight.Bold, color = textPrimary, fontSize = 24.sp)
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            IconButton(onClick = {}) { Icon(Icons.Default.Refresh, "Refresh", tint = textSecondary) }
                            IconButton(onClick = {}) { Icon(Icons.Default.Download, "Download CSV", tint = textSecondary) }
                        }
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                    
                    CostStackedBarChart(isDarkTheme)
                }
            }

            // Table section
            Card(
                colors = CardDefaults.cardColors(containerColor = cardBg),
                border = BorderStroke(1.dp, borderColor),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                CostTable(isDarkTheme)
            }
        }
    }
}

@Composable
fun DropdownFilterButton(label: String, value: String, isDarkTheme: Boolean) {
    val borderColor = if (isDarkTheme) BorderDark else BorderLight
    val textPrimary = if (isDarkTheme) TextDarkPrimary else TextLightPrimary
    val textSecondary = if (isDarkTheme) TextDarkSecondary else TextLightSecondary

    Column {
        Text(label, color = textSecondary, fontSize = 12.sp)
        Spacer(modifier = Modifier.height(4.dp))
        Row(
            modifier = Modifier
                .border(BorderStroke(1.dp, borderColor), RoundedCornerShape(4.dp))
                .clickable { }
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(value, color = textPrimary, fontSize = 14.sp)
            Spacer(modifier = Modifier.width(8.dp))
            Icon(Icons.Default.ArrowDropDown, contentDescription = null, tint = textSecondary, modifier = Modifier.size(16.dp))
        }
    }
}

@Composable
fun borderStroke(color: Color) : BorderStroke {
    return BorderStroke(1.dp, color)
}

@Composable
fun CostStackedBarChart(isDarkTheme: Boolean) {
    val textSecondary = if (isDarkTheme) TextDarkSecondary else TextLightSecondary
    val gridColor = if (isDarkTheme) Color(0xFF2C2A35) else Color(0xFFEAEAED)

    val data = listOf(
        listOf(40f, 15f, 10f, 8f, 5f),
        listOf(42f, 16f, 11f, 8f, 5f),
        listOf(45f, 15f, 10f, 8f, 5f),
        listOf(39f, 14f, 9f, 7f, 4f),
        listOf(38f, 14f, 9f, 7f, 4f),
        listOf(42f, 16f, 10f, 8f, 5f),
        listOf(46f, 17f, 11f, 9f, 6f),
        // Add more days to look like AWS
        listOf(48f, 18f, 12f, 9f, 6f),
        listOf(47f, 19f, 13f, 8f, 6f),
        listOf(45f, 17f, 11f, 8f, 5f)
    )
    val maxCost = 100f
    
    val colors = listOf(AwsBlue, AwsOrange, AwsGreen, AwsPurple, AwsRed)
    val labels = listOf("EC2-Instances", "Relational Database Service", "S3", "CloudWatch", "Other")

    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth().height(250.dp)
        ) {
            // Y-axis
            Column(
                modifier = Modifier.width(50.dp).fillMaxHeight().padding(bottom = 20.dp),
                verticalArrangement = Arrangement.SpaceBetween,
                horizontalAlignment = Alignment.End
            ) {
                Text("$100", color = textSecondary, fontSize = 10.sp)
                Text("$75", color = textSecondary, fontSize = 10.sp)
                Text("$50", color = textSecondary, fontSize = 10.sp)
                Text("$25", color = textSecondary, fontSize = 10.sp)
                Text("$0", color = textSecondary, fontSize = 10.sp)
            }
            
            Spacer(modifier = Modifier.width(8.dp))

            // Chart area
            val scrollState = rememberScrollState()
            Box(
                modifier = Modifier.weight(1f).fillMaxHeight()
                    .horizontalScroll(scrollState)
            ) {
                Canvas(
                    modifier = Modifier.width((data.size * 50).dp).fillMaxHeight().padding(bottom = 20.dp)
                ) {
                    val width = size.width
                    val height = size.height
                    
                    // Horizontal grid lines
                    for (i in 0..4) {
                        val y = height - (height * (i / 4f))
                        drawLine(
                            color = gridColor,
                            start = Offset(0f, y),
                            end = Offset(width, y),
                            strokeWidth = 1f
                        )
                    }

                    // Bars
                    val barWidth = 24.dp.toPx()
                    val spacing = (width - (data.size * barWidth)) / (data.size + 1)
                    
                    data.forEachIndexed { index, dayCosts ->
                        var currentY = height
                        val x = spacing + index * (barWidth + spacing)
                        
                        dayCosts.forEachIndexed { sIndex, cost ->
                            val segmentHeight = (cost / maxCost) * height
                            currentY -= segmentHeight
                            drawRoundRect(
                                color = colors[sIndex % colors.size],
                                topLeft = Offset(x, currentY),
                                size = Size(barWidth, segmentHeight),
                                cornerRadius = CornerRadius(1f, 1f)
                            )
                        }
                    }
                }
                
                // X-axis labels
                Row(
                    modifier = Modifier.width((data.size * 50).dp).align(Alignment.BottomStart).padding(top = 8.dp),
                ) {
                    data.forEachIndexed { index, _ ->
                        Box(modifier = Modifier.weight(1f), contentAlignment = Alignment.Center) {
                            Text("Nov ${10 + index}", color = textSecondary, fontSize = 10.sp)
                        }
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Legend
        Row(
            modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            labels.forEachIndexed { index, label ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(modifier = Modifier.size(12.dp).background(colors[index % colors.size], RoundedCornerShape(2.dp)))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(label, color = textSecondary, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
fun CostTable(isDarkTheme: Boolean) {
    val borderColor = if (isDarkTheme) BorderDark else BorderLight
    val textPrimary = if (isDarkTheme) TextDarkPrimary else TextLightPrimary
    val textSecondary = if (isDarkTheme) TextDarkSecondary else TextLightSecondary

    val services = listOf(
        "EC2 - Instances", "Relational Database Service", "S3", "CloudWatch", "Other"
    )
    val totalCosts = listOf("$1,245.80", "$450.20", "$320.15", "$250.00", "$190.74")
    
    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.background(if (isDarkTheme) Color(0xFF23222A) else Color(0xFFFAFAFA))
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Service", fontWeight = FontWeight.Bold, color = textSecondary, fontSize = 12.sp, modifier = Modifier.weight(1f))
            Text("Total Cost", fontWeight = FontWeight.Bold, color = textSecondary, fontSize = 12.sp, textAlign = TextAlign.End)
        }
        
        services.forEachIndexed { index, service ->
            Row(
                modifier = Modifier.fillMaxWidth()
                    .border(BorderStroke(0.5.dp, borderColor))
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(service, color = AwsBlue, fontSize = 14.sp, modifier = Modifier.weight(1f).clickable { })
                Text(totalCosts[index], color = textPrimary, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}
