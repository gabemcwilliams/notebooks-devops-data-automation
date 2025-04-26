 
    job "products_sophos_central_endpoint_api_alerts" {
    
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
            command = "C:/automation/venv/Scripts/python.exe"
            args    = [".py"]
          }
    
          dispatch_payload {
            file = ""
          }
    
        }
      }
    }    
    