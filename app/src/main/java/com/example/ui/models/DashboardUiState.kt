package com.example.ui.models

import com.example.api.models.DashboardSummary

data class DashboardUiState(
    val isLoading: Boolean = false,
    val data: DashboardSummary? = null,
    val error: String? = null
)
