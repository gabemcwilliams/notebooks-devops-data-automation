 
    job "products_auvik_api_tenants" {
    
      type = "batch"
    
      periodic {
        cron             = "30 * * * *"
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
    