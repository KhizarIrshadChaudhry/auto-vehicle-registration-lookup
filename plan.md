## Mulig applikationsstruktur:
auto-vehicle-registration-lookup/
  app/
    main.py
    ui/
      main_window.py
      widgets.py
    camera/
      camera_stream.py
    vision/
      plate_detector.py
      ocr_reader.py
      preprocess.py
      tracker.py
    services/
      database.py
      vehicle_api.py
      job_queue.py
    models/
      types.py
    config/
      settings.py
  data/
    snapshots/
    db/
  tests/
  requirements.txt

# Pipeline structure
1. Capture cam frame
2. Detect licencse plate
3. Crop plate
4. OCR on plate string
5. Normalize & Validate
6. Deduplicate - ensure that same plate does not get scanned
7. Store to DB
8. Call Vehicle API
9. Store API event & link to plate event
10. Show result in UI

## Step 2 - Detect license plate
Her kan der benyttes to metoder:
1. Programmatisk klassisk detection 
Her vil der nok benyttes grayscale og edge-detection teknikekr til at finde retanglen for plate detection.
2. ML Model
Her vil der optrænes en ML model til at returnere rektanglen for nummerpladen, givet et img som input. Det er typisk en YOLO baseret objekt detektions model der benyttes her. Allerede optrænet modeller kan evt. benyttes her. 
  