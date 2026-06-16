@file:OptIn(ExperimentalMaterial3Api::class)
package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
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
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.ui.CloudViewModel
import com.example.ui.screens.*
import com.example.ui.theme.*
import kotlinx.coroutines.launch

enum class CloudScreen(val title: String, val icon: ImageVector) {
    DASHBOARD("Dashboard", Icons.Default.Dashboard),
    AI("AI Engine", Icons.Default.SmartToy),
    SRE("SRE Plane", Icons.Default.Hub),
    HCL("HCL Migrate", Icons.Default.Code),
    GEMINI("AI", Icons.Default.Chat),
    CLOUD("Cloud Connectors", Icons.Default.Cloud),
    CLOUDSHELL("CloudShell", Icons.Default.Terminal)
}

@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
fun regionLabel(region: String): String {
    return when (region) {
        "ap-south-1" -> "Mumbai ($region)"
        "us-east-1" -> "N. Virginia ($region)"
        "ap-southeast-1" -> "Singapore ($region)"
        "eu-central-1" -> "Frankfurt ($region)"
        "ap-northeast-1" -> "Tokyo ($region)"
        "ap-northeast-2" -> "Seoul ($region)"
        "ap-northeast-3" -> "Osaka ($region)"
        "ca-central-1" -> "Canada ($region)"
        "eu-west-1" -> "Ireland ($region)"
        "eu-west-2" -> "London ($region)"
        "eu-west-3" -> "Paris ($region)"
        "us-west-1" -> "California ($region)"
        "us-west-2" -> "Oregon ($region)"
        else -> region
    }
}

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            var isDarkTheme by remember { mutableStateOf(false) } // False for Bento warmup, True for Cosmic black

            MyApplicationTheme(darkTheme = isDarkTheme) {
                val viewModel: CloudViewModel = viewModel()
                val jwtTokenState by viewModel.jwtToken.collectAsState()

                if (jwtTokenState.isNullOrEmpty()) {
                    LoginScreen(
                        viewModel = viewModel,
                        onLoginSuccess = {
                            // Token obtained, UI will automatically transition
                        }
                    )
                } else {
                    var currentScreen by remember { mutableStateOf(CloudScreen.DASHBOARD) }
                    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
                    val scope = rememberCoroutineScope()

                    ModalNavigationDrawer(
                        drawerState = drawerState,
                        drawerContent = {
                            ModalDrawerSheet(
                                modifier = Modifier.width(300.dp),
                                drawerContainerColor = if (isDarkTheme) Color(0xFF151419) else Color(0xFFF6F3FB)
                            ) {
                                Column(
                                    modifier = Modifier
                                        .fillMaxSize()
                                        .padding(24.dp)
                                ) {
                                    // Drawer Header
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        modifier = Modifier.padding(bottom = 16.dp)
                                    ) {
                                        Box(
                                            modifier = Modifier
                                                .size(42.dp)
                                                .clip(RoundedCornerShape(10.dp))
                                                .background(BentoPurplePrimary),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Memory,
                                                contentDescription = "CloudOps Logo",
                                                tint = Color.White,
                                                modifier = Modifier.size(24.dp)
                                            )
                                        }
                                        Spacer(modifier = Modifier.width(12.dp))
                                        Column {
                                            Text(
                                                text = "CLOUDOPS",
                                                fontSize = 18.sp,
                                                fontWeight = FontWeight.ExtraBold,
                                                color = if (isDarkTheme) Color.White else BentoTextDark,
                                                fontFamily = FontFamily.Monospace,
                                                letterSpacing = 1.sp
                                            )
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                Box(
                                                    modifier = Modifier
                                                        .size(8.dp)
                                                        .clip(CircleShape)
                                                        .background(Color(0xFF00FF66))
                                                )
                                                Spacer(modifier = Modifier.width(6.dp))
                                                Text(
                                                    text = "SRE Engine Active",
                                                    fontSize = 10.sp,
                                                    color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle,
                                                    fontWeight = FontWeight.SemiBold
                                                )
                                            }
                                        }
                                    }

                                    // Dynamic Operator SRE Profile Identity Card
                                    val currentUserEmail by viewModel.currentUserEmail.collectAsState()
                                    val currentOrgName by viewModel.currentOrgName.collectAsState()
                                    val currentUserRole by viewModel.currentUserRole.collectAsState()

                                    Card(
                                        colors = CardDefaults.cardColors(
                                            containerColor = if (isDarkTheme) Color(0xFF25232E) else Color(0xFFEADDFF).copy(alpha = 0.4f)
                                        ),
                                        shape = RoundedCornerShape(16.dp),
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(bottom = 16.dp)
                                            .testTag("drawer_profile_card")
                                    ) {
                                        Column(modifier = Modifier.padding(14.dp)) {
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                Icon(
                                                    imageVector = Icons.Default.AccountCircle,
                                                    contentDescription = "User Account",
                                                    tint = if (isDarkTheme) CyberCyan else BentoPurplePrimary,
                                                    modifier = Modifier.size(20.dp)
                                                )
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Text(
                                                    text = currentUserEmail ?: "unidentified@email.com",
                                                    fontSize = 12.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    color = if (isDarkTheme) Color.White else BentoTextDark,
                                                    maxLines = 1
                                                )
                                            }
                                            Spacer(modifier = Modifier.height(4.dp))
                                            Text(
                                                text = "Org: ${currentOrgName ?: "Operations Center"}",
                                                fontSize = 10.sp,
                                                fontWeight = FontWeight.Medium,
                                                color = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle
                                            )
                                            Box(
                                                modifier = Modifier
                                                    .padding(top = 8.dp)
                                                    .clip(RoundedCornerShape(6.dp))
                                                    .background(if (isDarkTheme) Color(0xFF0F0E13) else Color(0xFFFFE5EC))
                                                    .border(1.dp, if (isDarkTheme) CyberCyan.copy(alpha = 0.5f) else Color.Transparent, RoundedCornerShape(6.dp))
                                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                                            ) {
                                                Text(
                                                    text = "Access: ${currentUserRole ?: "ORG_ADMIN"}",
                                                    fontSize = 9.sp,
                                                    fontWeight = FontWeight.ExtraBold,
                                                    color = if (isDarkTheme) CyberCyan else Color(0xFFFF2B55),
                                                    fontFamily = FontFamily.Monospace
                                                )
                                            }
                                        }
                                    }

                                    Divider(color = if (isDarkTheme) Color(0xFF2C2A35) else BentoBorderLight, modifier = Modifier.padding(bottom = 12.dp))

                                    // Navigation List
                                    CloudScreen.values().filter { it != CloudScreen.AI }.forEach { screen ->
                                        val isSelected = currentScreen == screen
                                        NavigationDrawerItem(
                                            label = {
                                                Text(
                                                    text = screen.title,
                                                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                                    fontSize = 14.sp
                                                )
                                            },
                                            selected = isSelected,
                                            onClick = {
                                                currentScreen = screen
                                                scope.launch { drawerState.close() }
                                            },
                                            icon = {
                                                Icon(
                                                    imageVector = screen.icon,
                                                    contentDescription = screen.title,
                                                    tint = if (isSelected) {
                                                        if (isDarkTheme) CyberCyan else BentoPurpleDark
                                                    } else {
                                                        if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle
                                                    }
                                                )
                                            },
                                            colors = NavigationDrawerItemDefaults.colors(
                                                selectedContainerColor = if (isDarkTheme) Color(0xFF25232E) else BentoContainerActive,
                                                unselectedContainerColor = Color.Transparent,
                                                selectedIconColor = if (isDarkTheme) CyberCyan else BentoPurpleDark,
                                                selectedTextColor = if (isDarkTheme) Color.White else BentoTextDark,
                                                unselectedTextColor = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle
                                            ),
                                            modifier = Modifier
                                                .padding(vertical = 4.dp)
                                                .testTag("nav_item_${screen.name.lowercase()}"),
                                            shape = RoundedCornerShape(12.dp)
                                        )
                                    }

                                    // Terimate / Sign Out Operator
                                    NavigationDrawerItem(
                                        label = {
                                            Text(
                                                text = "Sign Out operator",
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 14.sp
                                            )
                                        },
                                        selected = false,
                                        onClick = {
                                            viewModel.logoutUser()
                                            scope.launch { drawerState.close() }
                                        },
                                        icon = {
                                            Icon(
                                                imageVector = Icons.Default.ExitToApp,
                                                contentDescription = "Sign Out Operator",
                                                tint = Color(0xFFFF2B55)
                                            )
                                        },
                                        colors = NavigationDrawerItemDefaults.colors(
                                            unselectedContainerColor = Color.Transparent,
                                            unselectedTextColor = Color(0xFFFF2B55)
                                        ),
                                        modifier = Modifier
                                            .padding(vertical = 4.dp)
                                            .testTag("nav_item_logout"),
                                        shape = RoundedCornerShape(12.dp)
                                    )

                                    Spacer(modifier = Modifier.weight(1f))

                                    // Theme switcher / footer inside drawer
                                    Row(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .clip(RoundedCornerShape(16.dp))
                                            .background(if (isDarkTheme) Color(0xFF0F0E13) else Color(0xFFEADDFF).copy(alpha = 0.4f))
                                            .clickable { isDarkTheme = !isDarkTheme }
                                            .padding(14.dp)
                                            .testTag("theme_toggle"),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Icon(
                                                imageVector = if (isDarkTheme) Icons.Default.LightMode else Icons.Default.DarkMode,
                                                contentDescription = "Theme Switch",
                                                tint = if (isDarkTheme) Color(0xFFFF9900) else BentoPurplePrimary,
                                                modifier = Modifier.size(20.dp)
                                            )
                                            Spacer(modifier = Modifier.width(10.dp))
                                            Text(
                                                text = if (isDarkTheme) "Bento Light Mode" else "Cosmic Dark Mode",
                                                fontSize = 12.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = if (isDarkTheme) Color.White else BentoTextDark
                                            )
                                        }
                                        Icon(
                                            imageVector = Icons.Default.ArrowForwardIos,
                                            contentDescription = "Go",
                                            modifier = Modifier.size(12.dp),
                                            tint = if (isDarkTheme) Color(0xFF9E9BA8) else BentoTextSubtitle
                                        )
                                    }
                                }
                            }
                        }
                    ) {
                        Scaffold(
                            topBar = {
                                @OptIn(ExperimentalMaterial3Api::class)
                                var regionExpanded by remember { mutableStateOf(false) }
                                val selectedRegion by viewModel.selectedRegion.collectAsState()
                                val regions by viewModel.regions.collectAsState()

                                TopAppBar(
                                    title = {},
                                    navigationIcon = {
                                        IconButton(
                                            onClick = { scope.launch { drawerState.open() } },
                                            modifier = Modifier.testTag("menu_button")
                                        ) {
                                            Icon(
                                                imageVector = Icons.Default.Menu,
                                                contentDescription = "Open Drawer",
                                                tint = if (isDarkTheme) Color.White else Color.Black
                                            )
                                        }
                                    },
                                    actions = {
                                        Box {
                                            Row(
                                                verticalAlignment = Alignment.CenterVertically,
                                                modifier = Modifier
                                                    .clickable { regionExpanded = true }
                                                    .padding(horizontal = 8.dp, vertical = 6.dp)
                                                    .testTag("region_selector")
                                            ) {
                                                Icon(
                                                    imageVector = Icons.Default.Public,
                                                    contentDescription = "Region Selector",
                                                    tint = if (isDarkTheme) Color.White else Color.Black,
                                                    modifier = Modifier.size(16.dp)
                                                )
                                                Spacer(modifier = Modifier.width(5.dp))
                                                Text(
                                                    text = selectedRegion,
                                                    fontWeight = FontWeight.Bold,
                                                    fontSize = 14.sp,
                                                    color = if (isDarkTheme) Color.White else Color.Black,
                                                    fontFamily = FontFamily.Monospace
                                                )
                                                Spacer(modifier = Modifier.width(3.dp))
                                                Icon(
                                                    imageVector = Icons.Default.KeyboardArrowDown,
                                                    contentDescription = "Select Region",
                                                    tint = if (isDarkTheme) Color.White else Color.Black,
                                                    modifier = Modifier.size(18.dp)
                                                )
                                            }

                                            LaunchedEffect(regions.size) {
                                                android.util.Log.e("REGION_UI", "Dropdown has ${regions.size} regions")
                                            }

                                            DropdownMenu(
                                                expanded = regionExpanded,
                                                onDismissRequest = { regionExpanded = false },
                                                modifier = Modifier.background(if (isDarkTheme) Color(0xFF151419) else Color.White)
                                            ) {
                                                regions.forEach { region ->
                                                    DropdownMenuItem(
                                                        text = {
                                                            Text(
                                                                text = regionLabel(region.name),
                                                                fontWeight = FontWeight.Bold,
                                                                color = if (isDarkTheme) {
                                                                    if (selectedRegion == region.name) CyberCyan else Color.White
                                                                } else {
                                                                    if (selectedRegion == region.name) Color.Black else BentoTextDark
                                                                }
                                                            )
                                                        },
                                                        onClick = {
                                                            viewModel.updateSelectedRegion(region.name)
                                                            regionExpanded = false
                                                        }
                                                    )
                                                }
                                            }
                                        }

                                        Spacer(modifier = Modifier.width(12.dp))

                                        // Premium AI Badge Button designed look wise better
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            modifier = Modifier
                                                .clip(RoundedCornerShape(12.dp))
                                                .clickable {
                                                    currentScreen = CloudScreen.GEMINI
                                                }
                                                .background(
                                                    if (isDarkTheme) Color(0xFF1E1C24) else Color(0xFFF3EFFF)
                                                )
                                                .border(
                                                    width = 1.5.dp,
                                                    color = if (isDarkTheme) Color(0xFFD500F9) else Color(0xFF6200EA),
                                                    shape = RoundedCornerShape(12.dp)
                                                )
                                                .padding(horizontal = 10.dp, vertical = 6.dp)
                                                .testTag("hexagon_logo_ai"),
                                            horizontalArrangement = Arrangement.Center
                                        ) {
                                            // Modern four-pointed vector sparkle
                                            Box(
                                                modifier = Modifier.size(12.dp),
                                                contentAlignment = Alignment.Center
                                            ) {
                                                androidx.compose.foundation.Canvas(modifier = Modifier.fillMaxSize()) {
                                                    val w = size.width
                                                    val h = size.height
                                                    val path = androidx.compose.ui.graphics.Path().apply {
                                                        moveTo(w / 2f, 0f)
                                                        quadraticTo(w / 2f, h / 2f, w, h / 2f)
                                                        quadraticTo(w / 2f, h / 2f, w / 2f, h)
                                                        quadraticTo(w / 2f, h / 2f, 0f, h / 2f)
                                                        quadraticTo(w / 2f, h / 2f, w / 2f, 0f)
                                                        close()
                                                    }
                                                    drawPath(
                                                        path = path,
                                                        color = if (isDarkTheme) Color(0xFF00E5FF) else Color(0xFF6200EA)
                                                    )
                                                }
                                            }
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Text(
                                                text = "AI",
                                                fontWeight = FontWeight.ExtraBold,
                                                fontSize = 12.sp,
                                                color = if (isDarkTheme) Color.White else Color.Black,
                                                fontFamily = FontFamily.SansSerif
                                            )
                                        }

                                        Spacer(modifier = Modifier.width(12.dp))

                                        // Command Line Terminal Outlined Box conforming to Image 2
                                        Box(
                                            modifier = Modifier
                                                .padding(end = 8.dp)
                                                .size(31.dp)
                                                .border(
                                                    width = 2.dp,
                                                    color = if (isDarkTheme) Color.White else Color.Black,
                                                    shape = RoundedCornerShape(8.dp)
                                                )
                                                .clickable {
                                                    currentScreen = CloudScreen.CLOUDSHELL
                                                }
                                                .testTag("terminal_refresh_button"),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Row(
                                                verticalAlignment = Alignment.CenterVertically,
                                                horizontalArrangement = Arrangement.Center
                                            ) {
                                                Text(
                                                    text = ">",
                                                    fontWeight = FontWeight.ExtraBold,
                                                    fontSize = 13.sp,
                                                    color = if (isDarkTheme) Color.White else Color.Black,
                                                    fontFamily = FontFamily.Monospace,
                                                    modifier = Modifier.offset(y = (-1).dp)
                                                )
                                                Box(
                                                    modifier = Modifier
                                                        .width(6.dp)
                                                        .height(2.dp)
                                                        .background(if (isDarkTheme) Color.White else Color.Black)
                                                        .offset(x = 1.dp, y = 4.dp)
                                                )
                                            }
                                        }
                                    },
                                    colors = TopAppBarDefaults.topAppBarColors(
                                        containerColor = if (isDarkTheme) Color(0xFF0F0E13) else Color.White,
                                        titleContentColor = if (isDarkTheme) Color.White else BentoTextDark
                                    )
                                )
                            }
                        ) { innerPadding ->
                            Box(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(innerPadding)
                                    .imePadding()
                                    .background(if (isDarkTheme) Color(0xFF0F0E13) else BentoBg)
                            ) {
                                when (currentScreen) {
                                    CloudScreen.DASHBOARD -> DashboardScreen(
                                        viewModel = viewModel,
                                        onNavigateToGraph = { currentScreen = CloudScreen.SRE }
                                    )
                                    CloudScreen.AI -> AiDoctorScreen(viewModel = viewModel)
                                    CloudScreen.SRE -> DependencyGraphScreen(
                                        viewModel = viewModel,
                                        onNavigateToGenerator = { currentScreen = CloudScreen.HCL }
                                    )
                                    CloudScreen.HCL -> TerraformGeneratorScreen(viewModel = viewModel)
                                    CloudScreen.GEMINI -> AiConsultantScreen(viewModel = viewModel)
                                    CloudScreen.CLOUD -> CloudConnectorsScreen(viewModel = viewModel)
                                    CloudScreen.CLOUDSHELL -> CloudShellScreen()
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
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(text = "Hello $name!", modifier = modifier)
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    MyApplicationTheme { Greeting("Android") }
}
