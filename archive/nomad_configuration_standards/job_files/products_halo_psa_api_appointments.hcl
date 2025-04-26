 
    job "products_halo_psa_api_appointments" {
    
      type = "batch"
    
      periodic {
        cron             = "45 * * * *"
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
    