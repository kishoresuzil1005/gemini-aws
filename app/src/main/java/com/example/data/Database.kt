package com.example.data

import android.content.Context
import androidx.room.*
import kotlinx.coroutines.flow.Flow

// --- entities ---

@Entity(tableName = "cloud_accounts")
data class CloudAccount(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val provider: String, // AWS, Azure, GCP
    val name: String,
    val credentialsHint: String,
    val region: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "discovery_resources")
data class DiscoveryResource(
    @PrimaryKey val id: String,
    val provider: String,
    val type: String, // EC2, RDS, S3, ECS, Lambda, VPC, ALB, etc.
    val name: String,
    val configurationHint: String,
    val costEstimate: Double,
    val dependenciesString: String // comma separated target IDs
)

@Entity(tableName = "saved_migrations")
data class SavedMigration(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val title: String,
    val sourceCloud: String,
    val targetCloud: String,
    val servicesMigrated: String,
    val terraformCode: String,
    val createdAt: Long = System.currentTimeMillis()
)

// --- DAOs ---

@Dao
interface CloudDao {
    // Cloud Accounts
    @Query("SELECT * FROM cloud_accounts ORDER BY createdAt DESC")
    fun getAllAccounts(): Flow<List<CloudAccount>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAccount(account: CloudAccount)

    @Query("DELETE FROM cloud_accounts WHERE id = :id")
    suspend fun deleteAccountById(id: Int)

    // Discovered Resources
    @Query("SELECT * FROM discovery_resources WHERE provider = :provider")
    fun getResourcesByProvider(provider: String): Flow<List<DiscoveryResource>>

    @Query("SELECT * FROM discovery_resources")
    fun getAllResources(): Flow<List<DiscoveryResource>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertResources(resources: List<DiscoveryResource>)

    @Query("DELETE FROM discovery_resources")
    suspend fun clearAllResources()

    // Saved Migrations
    @Query("SELECT * FROM saved_migrations ORDER BY createdAt DESC")
    fun getAllMigrations(): Flow<List<SavedMigration>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMigration(migration: SavedMigration)

    @Query("DELETE FROM saved_migrations WHERE id = :id")
    suspend fun deleteMigrationById(id: Int)
}

// --- Database Configuration ---

@Database(
    entities = [CloudAccount::class, DiscoveryResource::class, SavedMigration::class],
    version = 1,
    exportSchema = false
)
abstract class CloudDatabase : RoomDatabase() {
    abstract val dao: CloudDao

    companion object {
        @Volatile
        private var INSTANCE: CloudDatabase? = null

        fun getDatabase(context: Context): CloudDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    CloudDatabase::class.java,
                    "cloud_migrate_database"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}

// --- Repository Pattern ---

class CloudRepository(private val dao: CloudDao) {
    val allAccounts: Flow<List<CloudAccount>> = dao.getAllAccounts()
    val allResources: Flow<List<DiscoveryResource>> = dao.getAllResources()
    val allSavedMigrations: Flow<List<SavedMigration>> = dao.getAllMigrations()

    fun getResourcesForCloud(provider: String): Flow<List<DiscoveryResource>> {
        return dao.getResourcesByProvider(provider)
    }

    suspend fun insertAccount(account: CloudAccount) {
        dao.insertAccount(account)
    }

    suspend fun deleteAccount(id: Int) {
        dao.deleteAccountById(id)
    }

    suspend fun insertResources(resources: List<DiscoveryResource>) {
        dao.insertResources(resources)
    }

    suspend fun clearResources() {
        dao.clearAllResources()
    }

    suspend fun saveMigration(migration: SavedMigration) {
        dao.insertMigration(migration)
    }

    suspend fun deleteMigration(id: Int) {
        dao.deleteMigrationById(id)
    }
}
