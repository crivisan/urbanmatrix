<p align="center">
  <img src="icon_readme.png" alt="UrbanMatrix Logo" width="150"/>
</p>

<h1 align="center">UrbanMatrix</h1>
<p align="center">
  A QGIS plugin for spatial classification using the Matrix Method 🧮🏙️
</p>

---

## 💡 About the Plugin

**UrbanMatrix** helps urban planners and researchers apply the Matrix Method for multiple applications (Currently Developed for Building Density).\
It automates grid creation, layer import, building coverage analysis, classification, and styled visualization — all in one go.

---

## 🚀 Features

- 📐 Generate spatial grids of any resolution
- 🏢 Download and Postprocess Global ML Building Footprints from Microsoft
- 🧮 Calculate per-cell `application` --> currently implemented `Building Density`
- 🎯 Automatically assign Matrix Method risk classes
- 🎨 Predefined styling for buildings and classification results
- 🧼 Clean, minimal interface inside QGIS

---

## 🛠️ How to Use

1. Open QGIS
2. Open the UrbanMatrix panel (under Plugins)
3. Import or download a raster for background (optional)
4. Generate a grid over the visible extent
5. Download buildings or add your own feature layer
6. Run Matrix Method classification
7. Explore your results and export if needed


---

## 📷 Screenshots / Demos

<table>
  <tr>
    <td align="center">
      <img src="screenshot2.png" alt="UrbanMatrix Screenshot" width="310"/>
      <p><strong>Screenshot</strong></p>
    </td>
    <td align="center">
      <a href="https://youtu.be/xgnYrgwS6Fc">
        <img src="https://img.youtube.com/vi/xgnYrgwS6Fc/0.jpg" alt="Demo Video" width="400">
      </a>
      <p><strong><a href="https://youtu.be/xgnYrgwS6Fc">Watch Demo Video</a></strong></p>
    </td>
  </tr>
</table>

---
## 🧪 Current Status

This is a **beta release** — fully working but open for feedback and polish.  
You're welcome to try it, suggest improvements, or contribute!

---

## 🔧 Installation

### 📦 From QGIS Plugin Manager (Recommended)
1. Open QGIS
2. Go to **Plugins > Manage and Install Plugins**
3. Search for **UrbanMatrix**
4. Click **Install Plugin**

### 👩‍💻 Developer Mode (Manual Installation)
1. Clone or download this repository
2. Copy the folder to your QGIS plugin directory:
   - Windows: `C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - Linux/macOS: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS

---
## 🧩 Dependencies

UrbanMatrix uses the Python library [`mercantile`](https://pypi.org/project/mercantile/) to work with quadkeys and tile grids.

### 🛠 How to Install

If you're running QGIS on Windows, install it using the **OSGeo4W Shell**:
```bash
pip install mercantile
```
If you're on Linux/macOS with a standalone QGIS install, activate your environment and run the same command.


---

## 🙋 Author & Contact

**Developed by:** Cristhian Sanchez - DFKI\
**Email:** [crivisan1994@gmail.com](mailto:crivisan1994@gmail.com)  
**GitHub:** [github.com/crivisan](https://github.com/crivisan)\
**Linkedin:** [linkedin.com/crivisan](https://www.linkedin.com/in/crivisan/)

Feel free to reach out for questions, feedback, or collaborations
