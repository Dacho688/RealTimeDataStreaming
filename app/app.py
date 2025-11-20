import threading
import time
from functools import partial
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, LabelSet
from datetime import datetime
import random
import numpy as np

class BokehApp:
    def __init__(self, doc):
        self.doc = doc
        # Create a threading.Event to signal the thread to shut down
        self.stop_event = threading.Event()
        
        # Create a sample plot
        x = datetime.now()
        y = random.uniform(30, 500)
        self.source = ColumnDataSource(data=dict(x=[x], y=[y]))
        self.label_source = self.source.clone()
        p = figure(x_axis_type='datetime', 
                   width = 1800, 
                   height = 900,
                   x_axis_label="Time",
                   y_axis_label="Value",
                   title="Real Time Stock Price Streaming",
                   )
        p.title.align = "center"
        p.title.text_font_size="20px"
        p.toolbar.autohide = True
        p.line(x='x', y='y', source=self.source)
        p.scatter(x='x', y='y', source=self.source, size=8)

        #Create value Label
        label = LabelSet(x = 'x',
                         y = 'y', 
                         text= 'y', 
                        source = self.label_source,
                        x_offset=5, y_offset=5,
                        text_font_size="10pt")
        p.add_layout(label)
        # Start the background thread
        self.thread = threading.Thread(target=self.get_data, args=(self.stop_event,), daemon=True)
        self.thread.start()

        # Register the cleanup function
        self.doc.on_session_destroyed(self.on_session_destroyed)
        
        # Add the plot to the document
        self.doc.add_root(p)

    def get_data(self, stop_event):
        """
        Function to run in a separate thread.
        Infinite while loop until stop_event is set to True with on_session_destroyed().
        Simulates a long-running data-fetching task.
        """
        curr_value = self.source.data['y'][-1]
        log_curr_value = np.log(curr_value)

        while not stop_event.is_set():
            x = datetime.now()
            log_random_growth = random.normalvariate(mu=.00001, sigma=.001)
            log_y = log_curr_value + log_random_growth
            log_curr_value = log_y
            y = np.round(np.exp(log_curr_value),2)
            new_data = dict(x=[x], y=[y])
                
            # Safely schedule the update using a next tick callback
            self.doc.add_next_tick_callback(partial(self.update_plot, new_data))
            time.sleep(1)
        
        print("Background thread is shutting down gracefully.", flush=True)

    def update_plot(self, new_data):
        """
        This function is executed by the next tick callback on the main thread.
        It safely updates the ColumnDataSource.
        """
        self.source.stream(new_data, rollover=1000)
        self.label_source.data = new_data

    def on_session_destroyed(self, session_context):
        """
        Callback function that runs when a user closes the document.
        """
        print(f"Session {session_context.id} destroyed. Stopping background thread.", flush=True)
        self.stop_event.set()

# Create an instance of the class when the script is run by the Bokeh server
BokehApp(curdoc())
