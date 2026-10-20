package com.example.pincashybrid

data class BackupAttempt(val ok: Boolean, val error: String = "", val skipped: Boolean = false)
data class BackupSummary(val local: BackupAttempt, val cloud: BackupAttempt?) {
    val anySuccess: Boolean get() = local.ok || cloud?.ok == true
    val allConfiguredSucceeded: Boolean get() = local.ok && (cloud == null || cloud.ok)
}

/** A failure in either destination must never prevent attempting the other. */
object BackupCoordinator {
    fun run(local: () -> Boolean, cloud: (() -> Boolean)?): BackupSummary {
        fun attempt(write: () -> Boolean): BackupAttempt = try {
            BackupAttempt(true, skipped = !write())
        } catch (_: Exception) {
            BackupAttempt(false, "לא ניתן לשמור ולאמת את הקובץ. בדוק את התיקייה, ההרשאה והחיבור ונסה שוב.")
        }
        val localResult = attempt(local)
        val cloudResult = cloud?.let { attempt(it) }
        return BackupSummary(localResult, cloudResult)
    }
}
