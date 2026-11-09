import pandas as pd
import plotly.io as pio
import plotly.express as px

def Basic_example():
    pd.options.plotting.backend = "plotly"
    url = "https://raw.githubusercontent.com/uiuc-cse/data-fa14/gh-pages/data/iris.csv"
    Example = pd.read_csv(url)

    fig = px.scatter(   #Basic scatter plot
        Example, 
        x="sepal_width", 
        y="sepal_length", 
        color="species",
        title="Iris Sepal Length vs. Sepal Width",
        labels={"sepal_width": "Sepal Width (cm)", "sepal_length": "Sepal Length (cm)"}
    )
    
    fig3d = px.scatter_3d(    #Shows a 3d view of sepal length and width with petal length
        Example,
        x="sepal_width", 
        y="sepal_length", 
        z = "petal_length",
        color="species",
        title="3D Analysis of Iris Characteristics",
        labels={"petal_length": "Petal Length (cm)"}
    )

    ultimate = px.scatter_matrix(   #Comparing the graphs against each other
        Example,
        dimensions=["sepal_width", "sepal_length", "petal_width", "petal_length"],
        color="species",
        title="Iris Dataset Scatter Plot Matrix (SPLOM)"
    )
    ultimate.update_layout(width=900, height=900)
    ultimate.show()

Basic_example()