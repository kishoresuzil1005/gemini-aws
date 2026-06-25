package com.example.api.models

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class DashboardSummary(
    val region: String? = null,

    val total_resources: Int = 0,
    val running_resources: Int = 0,
    val stopped_resources: Int = 0,

    val region_count: Int = 0,
    val provider_count: Int = 0,

    val ec2: Int = 0,
    val s3: Int = 0,
    val rds: Int = 0,
    val lambda: Int = 0,
    val vpc: Int = 0,
    val iam: Int = 0,
    val ebs: Int = 0,

    val service_breakdown: Map<String, Int> = emptyMap()
)
