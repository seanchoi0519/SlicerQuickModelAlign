# QuickModelAlign

This is a 3D Slicer extension that allows for rapid alignment and comparison (visual & metric) of two 3D models using ALPACA's point-cloud based alignment capabilities.

It is freely usable, without any restrictions.

<img width="983" alt="Screen Shot 2023-05-31 at 2 50 54 am" src="https://github.com/seanchoi0519/SlicerQuickAlign/assets/33897705/56f2cdb4-c033-4156-853b-6ff4efbe1978">


## Installation

- Download and install a latest stable version of 3D Slicer [https://download.slicer.org]
- Start 3D Slicer application, open the Extension Manager (menu: View/Extension manager)
- Install **QuickModelAlign** extension

## How to cite

If you use QuickModelAlign in your research, please cite this publication.
- Choi, S, Choi, J, Peters, OA, Peters, CI. Design of an interactive system for access cavity assessment: A novel feedback tool for preclinical endodontics. Eur J Dent Educ. 2023; 00: 1- 9. doi:10.1111/eje.12895 (Open access)

## Tutorial
- Start 3D Slicer
- Switch to "QuickModelAlign" module (Modules > Registration > QuickModelAlign). If first time opening the module, wait for additional installations to complete 
- Import two 3D model files (supports .ply format only - for now) to compare on the left tab
- Click 'Load Models': The two models will be reduced to point-cloud based representation, ready for alignment
- Click 'Align Models': Wait about 5 seconds for software to run alignment & analysis
- Inspect results. Press '1', '2', '3' to navigate between different display mode options.
- Press 'spacebar' to start & stop animation.

### User Interface Overview

<img width="852" alt="Screen Shot 2023-05-31 at 3 00 13 am" src="https://github.com/seanchoi0519/SlicerQuickAlign/assets/33897705/5c2f7fdc-0461-4caf-a2ea-169ea3f7d2d5">

## Visualize and Analyze results
There are 3 display modes available to visualize and analyze the comparison results
### 1. Normal Mode (Default)

<img width="633" alt="Screen Shot 2023-05-31 at 2 44 28 am" src="https://github.com/seanchoi0519/SlicerQuickAlign/assets/33897705/b0ae5efa-1cf2-465f-aa62-db7723ae33e2">

- The advantage of this mode is that it allows the most simple visualization of the aligned models.
To enable this display mode, press "1" on keyboard

### 2. Wireframe Mode

<img width="882" alt="Screen Shot 2023-05-31 at 2 26 38 am" src="https://github.com/seanchoi0519/SlicerQuickAlign/assets/33897705/7e96ed5c-c24f-45c9-9f71-3fd379fc2ad9">

- The advantage of this display mode is that it allows visualization of the internal layers and structures of the aligned models.
To enable this display mode, press "2" on keyboard

### 3. Colour Map Mode

<img width="509" alt="Screen Shot 2023-05-31 at 2 26 45 am" src="https://github.com/seanchoi0519/SlicerQuickAlign/assets/33897705/9f337404-55ba-49ce-9403-6368d2ce0665">

- The advantage of this display mode is that it visually highlights areas of difference between the aligned models in colors (Red/Blue).
- Colour 'Red': highlights areas in the 'Prepared" model' that are excess or "under-prepared" compared to the ideal.
- Colour 'Blue': highlights areas in the "Prepared" model that are deficient or "over-prepared" compared to the 'Ideal' model.
- To enable this display mode, press "3" on keyboard

### Animation

- Note that by default, there is a live animation that goes back and forth between the two models to aid in visualization.
To start or stop the animation, press "spacebar" on keyboard

### Measurement

- Note that precise measurements of the models can be done via the ruler function (lower-left tab). 
- To delete the measurement, click the 'trash' icon.

## Advanced Settings

### Error Tolerance

- Error tolerance (mm) can be adjusted under "advanced settings" header in the left tab.
The concept of error tolerance is that it takes into account possible micro-errors in the alignment, or during the scanning & capturing of 3D data. In the colour map mode, only differences exceeding this error tolerance will be highlighted in color (red/blue). The initial value is set to 0.15mm (recommended).

## Publications

- Choi, S, Choi, J, Peters, OA, Peters, CI. Design of an interactive system for access cavity assessment: A novel feedback tool for preclinical endodontics. Eur J Dent Educ. 2023; 00: 1- 9. doi:10.1111/eje.12895

## Acknowledgments

- This module is built using Slicermorph - ALPACA as a foundation for the registration capability (developed by Arthur Porto, Sara Rolfe, and Murat Maga) [https://doi.org/10.1111/2041-210X.13689]
- Dr. Sean Choi has led development of this extension project to enable quick, simple alignment of 3D models, and the various visual display modes. Thank you also to Prof. Ove Peters (UQ), and Dr. Christine Peters (UQ), and Dr. Ryan Choi (UQ) for significant contributions to the development of this extension.

## Questions or Inquiries

- Please direct all development & collaboration inquires to Dr. Sean Choi: seanchoi05@gmail.com via email. 

## Copyright and Licensing

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

