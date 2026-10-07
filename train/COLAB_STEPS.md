# PathSense: Google Colab Training Quick Guide

## Academic Context
- **Project:** PathSense: Real-Time Edge-Vision for Road Condition Mapping
- **Academic Milestone:** 7th Semester Minor Project, CS-AI Department, SKIT Jaipur
- **Team Members:**
  1. Sharafat Khan (`23ESKCA098`)
  2. Soham Manocha (`23ESKCA102`)
  3. Sourabh Nagar (`23ESKCA105`)
  4. Vedic Baurasi (`23ESKCA119`)

---

## How to Run the Training Notebook in 3 Simple Steps:

### Step 1: Open Google Colab
1. Go to **[https://colab.research.google.com/](https://colab.research.google.com/)** in your browser.
2. Click on the **Upload** tab (या File -> Upload notebook).
3. Select this notebook file from your computer:
   📁 `C:\Users\nagar\OneDrive\Desktop\pathsense\train\PathSense_Colab_Training.ipynb`

### Step 2: Enable Free GPU
1. In Google Colab top menu, click **Runtime** $\rightarrow$ **Change runtime type**.
2. Select **T4 GPU** under Hardware accelerator.
3. Click **Save**.

### Step 3: Run the Cells
- Run cells sequentially (`Shift + Enter`).
- Colab will use its high-speed cloud connection (100+ MB/s) and NVIDIA T4 GPU to train the model.
- At the final step, it will automatically prompt you to download **`best.pt`** directly to your computer!

---

## After Downloading `best.pt`:
Copy the downloaded `best.pt` file into your local project directory:
`C:\Users\nagar\OneDrive\Desktop\pathsense\core\best.pt`

Then your live edge camera, video pipeline, and Streamlit dashboard will automatically use your fine-tuned weights!
