 
    job "products_datto_rmm_api_montors" {
    
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
            command = "C:/automation/venv/Scripts/python.exe"
            args    = [".py"]
          }
    
          dispatch_payload {
            file = ""
          }
    
        }
      }
    }    
    