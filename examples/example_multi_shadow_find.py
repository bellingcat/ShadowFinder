from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from shadowfinder import multi_shadow_find, plot_multi_shadows, ShadowFinder


def main():
    shadow_A = {
        "object_height": 10,
        "shadow_length": 8,
        "date_time": datetime(2024, 2, 29, 12, 0, 0),
    }
    shadow_B = {
        "object_height": 10,
        "shadow_length": 8.5,
        "date_time": datetime(2024, 2, 29, 13, 0, 0),
    }

    shadow_C = {
        "object_height": 10,
        "shadow_length": 9,
        "date_time": datetime(2024, 2, 29, 15, 0, 0),
    }

    finder = ShadowFinder()
    # check if timezones.npz exists
    try:
        finder.load_timezone_grid()
    except FileNotFoundError:
        finder.generate_timezone_grid()
        finder.save_timezone_grid()

    finder.set_details(**shadow_A, time_format="local")
    finder.find_shadows()
    fig_A = finder.plot_shadows()

    finder.set_details(**shadow_B, time_format="local")
    finder.find_shadows()
    fig_B = finder.plot_shadows()

    finder.set_details(**shadow_C, time_format="local")
    finder.find_shadows()
    fig_C = finder.plot_shadows()

    normalized_output = multi_shadow_find(
        [shadow_A, shadow_B, shadow_C], num_cores=2, time_format="local"
    )
    multi_shadow_fig = plot_multi_shadows(normalized_output)

    # Create a new figure with subplots
    fig, axs = plt.subplots(1, 4, figsize=(15, 5))

    # Plot fig_A
    fig_A.canvas.draw()
    axs[0].imshow(np.array(fig_A.canvas.renderer.buffer_rgba()))
    axs[0].set_title("Shadow A")

    # Plot fig_B
    fig_B.canvas.draw()
    axs[1].imshow(np.array(fig_B.canvas.renderer.buffer_rgba()))
    axs[1].set_title("Shadow B")

    # Plot fig_B
    fig_C.canvas.draw()
    axs[2].imshow(np.array(fig_B.canvas.renderer.buffer_rgba()))
    axs[2].set_title("Shadow C")

    # Plot multi_shadow_fig
    multi_shadow_fig.canvas.draw()
    axs[3].imshow(np.array(multi_shadow_fig.canvas.renderer.buffer_rgba()))
    axs[3].set_title("Multi Shadow")

    # Save the figure
    plt.savefig("example_multi_shadow_find_figure.png")

    # Display the figure
    plt.show()


if __name__ == "__main__":
    main()
