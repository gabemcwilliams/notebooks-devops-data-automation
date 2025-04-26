 
    job "datto_rmm_operating_systems_lifecycle" {
    
      type = "batch"
    
      periodic {
        cron             = "15 * * * *"
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
    