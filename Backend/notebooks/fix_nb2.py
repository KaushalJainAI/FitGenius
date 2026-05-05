import json
import os

nb_path = 'c:/Users/91700/Desktop/RS/Project/Backend/notebooks/data_analysis.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Just modifying the source code of the cells to monkey patch the OptionError issue
# Or simply remove sns.pairplot and use robust seaborn alternatives
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell.get('source', []))
        if 'sns.pairplot' in source:
            cell['source'] = [
                "# 4. Pairplot for Key Metrics\n",
                "try:\n",
                "    sns.pairplot(df[['Age', 'BMI', 'Calories_Burned', 'Experience_Level']], hue='Experience_Level', corner=True)\n",
                "    plt.show()\n",
                "except Exception as e:\n",
                "    print('Pairplot skipped due to local package version conflicts:', e)\n",
                "    # Fallback to pandas scatter_matrix\n",
                "    pd.plotting.scatter_matrix(df[['Age', 'BMI', 'Calories_Burned']], figsize=(10, 8), diagonal='kde')\n",
                "    plt.show()\n"
            ]
        elif 'import pandas as pd' in source and 'import os' in source:
            cell['source'] = [
                "import pandas as pd\n",
                "# Monkeypatch for Seaborn/Pandas 2.2 OptionError\n",
                "try:\n",
                "    pd.options.mode.use_inf_as_na = True\n",
                "    # Add a dummy option if seaborn requests it\n",
                "    if not hasattr(pd.options.mode, 'use_inf_as_null'):\n",
                "        pd.options.mode.use_inf_as_null = True\n",
                "except Exception:\n",
                "    pass\n",
                "\n",
                "import numpy as np\n",
                "import pickle\n",
                "import os\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "import warnings\n",
                "warnings.filterwarnings('ignore')\n",
                "\n",
                "from sklearn.neighbors import NearestNeighbors\n",
                "from sklearn.preprocessing import StandardScaler, OneHotEncoder\n",
                "from sklearn.compose import ColumnTransformer\n",
                "\n",
                "# Setup Paths\n",
                "DATA_PATH = './data/gym_members_exercise_tracking.csv'\n",
                "MODEL_DIR = '../recommendations/models/'\n",
                "os.makedirs(MODEL_DIR, exist_ok=True)\n",
                "\n",
                "# Set premium aesthetic style for charts\n",
                "sns.set_theme(style='darkgrid', palette='muted')\n",
                "plt.rcParams['figure.figsize'] = (10, 6)\n"
            ]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Patched data_analysis.ipynb successfully.')
