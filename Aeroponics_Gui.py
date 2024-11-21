
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox, Tk, StringVar, OptionMenu, Button, Label, Frame, Toplevel
from tkinter import ttk
from tkcalendar import DateEntry
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Global variable for the dataframe
df = None

# Load CSV file and clean column names
def load_file():
    global df
    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    if file_path:
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip().str.replace('[^A-Za-z0-9 ]+', '', regex=True).str.replace(' ', '_')
            messagebox.showinfo("Success", "File loaded and cleaned successfully!")
            update_column_options()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

# Update dropdown options based on dataframe columns
def update_column_options():
    if df is not None:
        columns = df.columns.tolist()
        column_var.set(columns[0])
        column_menu['menu'].delete(0, 'end')
        for col in columns:
            column_menu['menu'].add_command(label=col, command=lambda value=col: column_var.set(value))

# Filter data by date range
# Plot all columns against 'Timestamp'
# Plot all columns against 'Timestamp'
def plot_data():
    filtered_df = filter_data()
    if filtered_df is not None:
        columns_to_plot = [col for col in filtered_df.columns if col != 'Timestamp']
        num_plots = len(columns_to_plot)
        num_cols = 2  # Number of columns per row
        num_rows = (num_plots // num_cols) + (num_plots % num_cols > 0)  # Calculate required rows

        # Dynamically adjust figure size based on number of rows
        fig, axs = plt.subplots(num_rows, num_cols, figsize=(10, max(3, num_rows * 3)))
        fig.suptitle('All Data Plots', fontsize=16, y=0.98)

        axs = axs.flatten()  # Flatten axs for easy iteration

        # for idx, col in enumerate(columns_to_plot):
        #     axs[idx].plot(filtered_df['Timestamp'], filtered_df[col], color=color_var.get(), marker=marker_var.get())
        #     axs[idx].set_title(f"{col}", fontsize=10)
        #     axs[idx].set(xlabel='Timestamp', ylabel=col)
            
        #     # Format x-axis ticks with reduced size and rotation
        #     # axs[idx].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x).strftime('%H:%M:%S')))
        #     axs[idx].tick_params(axis='x', rotation=0, labelsize=5)
        for idx, col in enumerate(columns_to_plot):
            
            axs[idx].plot(filtered_df['Timestamp'], filtered_df[col], 
                        color=color_var.get() if color_var else 'blue', 
                        marker=marker_var.get() if marker_var else 'o')
            axs[idx].set_title(f"{col}", fontsize=10)
            axs[idx].set(xlabel='Timestamp', ylabel=col)

            # Format x-axis ticks without overlap
            try:
                axs[idx].xaxis.set_major_locator(plt.MaxNLocator(nbins=6))  # Limit to 6 ticks to prevent overlap
                # axs[idx].xaxis.set_major_formatter(plt.FuncFormatter(
                #     lambda x, _: pd.to_datetime(x).strftime('%H:%M:%S')
                # ))
            except Exception as e:
                axs[idx].set_xlabel('Timestamp (Invalid Format)')
                print(f"Error formatting x-axis: {e}")
            
            # Keep x-axis labels without rotation
            axs[idx].tick_params(axis='x', rotation=0, labelsize=6)


        # Remove unused subplots
        for ax in axs[num_plots:]:
            ax.remove()

        # Adjust padding and spacing for better fit
        plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2, hspace=0.6, wspace=0.4)

        # Clear previous plot and add the new figure to the GUI
        for widget in plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


def filter_data():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    if 'Timestamp' in df.columns:
        try:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
            filtered_df = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]
            if filtered_df.empty:
                messagebox.showinfo("Info", "No data available for the selected date range.")
            return filtered_df
        except Exception as e:
            messagebox.showerror("Error", f"Date filtering failed: {str(e)}")
    else:
        messagebox.showerror("Error", "Timestamp column not found!")

# Display column statistics
# def calculate_statistics():
#     selected_column = column_var.get()
#     if selected_column in df.columns:
#         stats = df[selected_column].describe()
#         stats_window = Toplevel(root)
#         stats_window.title("Statistics")
#         stats_window.geometry("300x200")
#         for stat, value in stats.items():
#             Label(stats_window, text=f"{stat}: {value:.4f}", font=('Arial', 10)).pack(pady=5)
def calculate_statistics():
    selected_column = column_var.get()
    if selected_column in df.columns:
        stats = df[selected_column].describe()
        stats_window = Toplevel(root)
        stats_window.title("Statistics")
        stats_window.configure(bg="black")
        Label(stats_window, text=f"Statistics for {selected_column}", font=('Arial', 14, 'bold'), fg="white", bg="black").pack(pady=10)
        for stat, value in stats.items():
            Label(stats_window, text=f"{stat}: {value:.4f}", font=('Arial', 12), fg="lightgrey", bg="black").pack()            

# # Plot all columns against 'Timestamp'
# def plot_data():
#     filtered_df = filter_data()
#     if filtered_df is not None:
#         columns_to_plot = [col for col in filtered_df.columns if col != 'Timestamp']
#         num_plots = len(columns_to_plot)
#         num_cols = 2  # Adjust columns per row here for flexibility
#         num_rows = (num_plots // num_cols) + (num_plots % num_cols > 0)  # Calculate required rows
        
#         fig, axs = plt.subplots(num_rows, num_cols, figsize=(12, num_rows * 3))  # Dynamically adjust figure height
#         fig.suptitle('All Data Plots', fontsize=16, y=1.05)
        
#         axs = axs.flatten()  # Flatten axs for easy iteration

#         for idx, col in enumerate(columns_to_plot):
#             axs[idx].plot(filtered_df['Timestamp'], filtered_df[col], color=color_var.get(), marker=marker_var.get())
#             axs[idx].set_title(f"{col}")
#             axs[idx].set(xlabel='Timestamp', ylabel=col)

#         for ax in axs[num_plots:]:
#             ax.remove()

#         plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.4, wspace=0.3)
        
#         for widget in plot_frame.winfo_children():
#             widget.destroy()

#         canvas = FigureCanvasTkAgg(fig, master=plot_frame)
#         canvas.draw()
#         canvas.get_tk_widget().pack(fill="both", expand=True)

# Linear Regression Function
def linear_regression_analysis():
    if df is None:
        messagebox.showerror("Error", "No data loaded!")
        return
    
    dependent_var = column_var.get()  # Dependent variable
    if dependent_var not in df.columns:
        messagebox.showerror("Error", "Select a valid dependent variable!")
        return
    
    independent_vars = [col for col in df.columns if col not in ['Timestamp', dependent_var]]
    if not independent_vars:
        messagebox.showerror("Error", "No independent variables available!")
        return

    X = df[independent_vars].fillna(df[independent_vars].mean())
    y = df[dependent_var].fillna(df[dependent_var].mean())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    results_window = Toplevel(root)
    results_window.title("Linear Regression Results")
    results_window.geometry("400x300")
    Label(results_window, text=f"Dependent Variable: {dependent_var}", font=('Arial', 12)).pack(pady=10)
    Label(results_window, text=f"Independent Variables: {', '.join(independent_vars)}", font=('Arial', 12)).pack(pady=10)
    Label(results_window, text=f"RMSE: {rmse:.4f}", font=('Arial', 12)).pack(pady=10)
    Label(results_window, text=f"R² Score: {r2:.4f}", font=('Arial', 12)).pack(pady=10)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.5)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], color='red', linewidth=2)
    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.title("Actual vs Predicted Values")
    plt.show()

# Main Window Setup
root = Tk()
root.title("Advanced Data Plotter")
root.geometry("1200x800")

main_frame = Frame(root, bg="#1e1e1e")
main_frame.pack(fill="both", expand=True)
sidebar = Frame(main_frame, bg="#333333", padx=15, pady=15, width=250)
sidebar.pack(side="left", fill="y")

toggle_button = Button(main_frame, text="Hide Sidebar", command=lambda: sidebar.pack_forget() if sidebar.winfo_ismapped() else sidebar.pack(side="left"), font=('Arial', 10, 'bold'), bg="#007acc", fg="white")
toggle_button.pack(side="top", anchor="ne", pady=5, padx=10)

Label(sidebar, text="Controls", font=('Arial', 16, 'bold'), fg="lightgrey", bg="#333333").pack(pady=15)
Button(sidebar, text="Load CSV File", command=load_file, font=('Arial', 10), bg="#555555", fg="white").pack(pady=10)
Label(sidebar, text="Select Column for Linear Dependent:", font=('Arial', 12), fg="lightgrey", bg="#333333").pack(pady=5)
column_var = StringVar(root)
column_menu = ttk.OptionMenu(sidebar, column_var, "")
column_menu.pack(pady=10)

Label(sidebar, text="Start Date:", font=('Arial', 12), fg="lightgrey", bg="#333333").pack(pady=5)
start_date_entry = DateEntry(sidebar, selectmode='day', date_pattern='dd/mm/yyyy', font=('Arial', 10))
start_date_entry.pack(pady=5)
Label(sidebar, text="End Date:", font=('Arial', 12), fg="lightgrey", bg="#333333").pack(pady=5)
end_date_entry = DateEntry(sidebar, selectmode='day', date_pattern='dd/mm/yyyy', font=('Arial', 10))
end_date_entry.pack(pady=5)
# Plot Customization Variables
color_var = StringVar(value="blue")  # Default plot color
marker_var = StringVar(value="o")   # Default marker style

# Dropdown for Color Selection
Label(sidebar, text="Select Plot Color:", font=('Arial', 12), fg="lightgrey", bg="#333333").pack(pady=5)
color_menu = ttk.OptionMenu(sidebar, color_var, "blue", "blue", "red", "green", "black", "orange")
color_menu.pack(pady=5)

# Dropdown for Marker Selection
Label(sidebar, text="Select Marker Style:", font=('Arial', 12), fg="lightgrey", bg="#333333").pack(pady=5)
marker_menu = ttk.OptionMenu(sidebar, marker_var, " ", "o", "s", "d", "*", "+", "x")
marker_menu.pack(pady=5)


Button(sidebar, text="Plot Data", command=plot_data, font=('Arial', 10), bg="#555555", fg="white").pack(pady=10)
Button(sidebar, text="Show Statistics", command=calculate_statistics, font=('Arial', 10), bg="#555555", fg="white").pack(pady=10)
Button(sidebar, text="Run Linear Regression", command=linear_regression_analysis, font=('Arial', 10), bg="#555555", fg="white").pack(pady=10)

plot_frame = Frame(main_frame, bg="#1e1e1e", padx=15, pady=15)
plot_frame.pack(side="right", fill="both", expand=True)

root.mainloop()
