job "datto_rmm_api_monthly_reports_ms_patching" {

  type = "batch"

  periodic {
    cron             = "0 * * * *"
    prohibit_overlap = true
  }

  group "data_pipeline" {
    count = 1
    task "ETL" {
      driver = "raw_exec"

      config {
        command = "D:/Git/example_infrastructure_data_dev/env/Scripts/python.exe"
        args    = [".py"]
      }

      dispatch_payload {
        file = ""
      }

    }
  }
}

