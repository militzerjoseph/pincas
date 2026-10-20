package com.example.pincashybrid

import org.junit.Assert.*
import org.junit.Test

class BackupCoordinatorTest {
    @Test fun cloudStillRunsWhenLocalThrows() {
        var cloudCalled = false
        val r = BackupCoordinator.run({ error("local failed") }, { cloudCalled = true; true })
        assertTrue(cloudCalled)
        assertFalse(r.local.ok)
        assertTrue(r.cloud!!.ok)
        assertTrue(r.anySuccess)
        assertFalse(r.allConfiguredSucceeded)
    }
    @Test fun cloudFailureDoesNotEraseLocalSuccess() {
        val r = BackupCoordinator.run({ true }, { error("offline") })
        assertTrue(r.local.ok)
        assertFalse(r.cloud!!.ok)
        assertTrue(r.anySuccess)
        assertFalse(r.allConfiguredSucceeded)
    }
    @Test fun skippedProgramIsVerifiedSuccessWithoutNewCopy() {
        val r = BackupCoordinator.run({ false }, { false })
        assertTrue(r.allConfiguredSucceeded)
        assertTrue(r.local.skipped)
        assertTrue(r.cloud!!.skipped)
    }
    @Test fun bothFailuresNeverReportSuccess() {
        val r = BackupCoordinator.run({ error("local") }, { error("cloud") })
        assertFalse(r.anySuccess)
        assertFalse(r.allConfiguredSucceeded)
    }
    @Test fun noCloudRemainsAnExplicitMissingDestination() {
        val r = BackupCoordinator.run({ true }, null)
        assertNull(r.cloud)
        assertTrue(r.local.ok)
    }
}

