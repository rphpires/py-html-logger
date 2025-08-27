import htmllogger 


def main():
    # Example usage of the logging functions
    log("This is an informational message.")
    log("This is a warning message.", color="yellow")
    error("This is an error message.")

    try:
        # Simulate an exception
        1 / 0
    except Exception as ex:
        report_exception(ex)


if __name__ == "__main__":
    main()
