cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(QuickModelAlign)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/seanchoi0519/SlicerQuickModelAlign#readme")
set(EXTENSION_CATEGORY "QuickModelAlign")
set(EXTENSION_CONTRIBUTORS "Arthur Porto (LSU), Sara Rolfe (UW), Murat Maga (SCRI), Dr. Sean Choi (UQ)")
set(EXTENSION_DESCRIPTION "QuickModelAlign allows a quick, simple alignment and comparison of two 3D models aided by ALPACA and custom display modes.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/seanchoi0519/SlicerQuickModelAlign/master/QuickModelAlign.png")
set(EXTENSION_SCREENSHOTURLS
  # User Interface Overview
  "https://private-user-images.githubusercontent.com/33897705/242237458-5c2f7fdc-0461-4caf-a2ea-169ea3f7d2d5.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTQ2MzI3NjIsIm5iZiI6MTcxNDYzMjQ2MiwicGF0aCI6Ii8zMzg5NzcwNS8yNDIyMzc0NTgtNWMyZjdmZGMtMDQ2MS00Y2FmLWEyZWEtMTY5ZWEzZjdkMmQ1LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MDIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTAyVDA2NDc0MlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWQ2NTk0NjBlMTRkZDlmZmRmNmRlOTFmOThmMDUxYzcyMTg1NjAyZTRhNDhhZDUzOTgxNTY3ZGE0NzhlZGQxYjEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.BYqp0gms8jlhfdQsWkU-fcag4XUJW-TFvzARQjKBpdI"
  # Normal Mode
  "https://private-user-images.githubusercontent.com/33897705/242236203-b0ae5efa-1cf2-465f-aa62-db7723ae33e2.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTQ2MzI3NjIsIm5iZiI6MTcxNDYzMjQ2MiwicGF0aCI6Ii8zMzg5NzcwNS8yNDIyMzYyMDMtYjBhZTVlZmEtMWNmMi00NjVmLWFhNjItZGI3NzIzYWUzM2UyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MDIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTAyVDA2NDc0MlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTFlNGI0NWU1YTc0OTQ0ZjRiZTc1YjEwNzFhMWE3ZDhjZTExYzk3OWE4Yjk3ZWY2NGY3MDJhYjA5MTU2ZDY1YjMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.0e-ZI7xqlgeBjXsdfxeTiUCbroWWS3RlIhqcdZo8M88"
  # Wireframe Mode
  "https://private-user-images.githubusercontent.com/33897705/242236111-7e96ed5c-c24f-45c9-9f71-3fd379fc2ad9.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTQ2MzI3NjIsIm5iZiI6MTcxNDYzMjQ2MiwicGF0aCI6Ii8zMzg5NzcwNS8yNDIyMzYxMTEtN2U5NmVkNWMtYzI0Zi00NWM5LTlmNzEtM2ZkMzc5ZmMyYWQ5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MDIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTAyVDA2NDc0MlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWFiMDJjNWFhN2E1Y2ZjY2VkMjJlMDUyOTAyZWE2NTEzNTU1NTlhYzUzOTY1ODA4Y2M5YzhlZmExMTVlZTk2OWMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.yw2s6Qg7lG8RiSoPtikUHE6XcdYsyfMIb5h2BogjVVs"
  # Colour Map Mode
  "https://private-user-images.githubusercontent.com/33897705/242236262-9f337404-55ba-49ce-9403-6368d2ce0665.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTQ2MzI3NjIsIm5iZiI6MTcxNDYzMjQ2MiwicGF0aCI6Ii8zMzg5NzcwNS8yNDIyMzYyNjItOWYzMzc0MDQtNTViYS00OWNlLTk0MDMtNjM2OGQyY2UwNjY1LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MDIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTAyVDA2NDc0MlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTM2NzlkMjc5N2YwMTkwZDU1NmJlMTQyZGIzMWZkN2YxYTUwZjZhODc2M2M2MjYyZmMyMzdlYjhhZDE4NDVlYmQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.XO4_gT3wJSgsLYcAHxw8RAe9FS4n3nMGcuPL7aG0Y-0"
)
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(QuickModelAlign)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})

