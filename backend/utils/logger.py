import logging


def setup_logger(app):
    """Configure app logger (console only for MVP)."""
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(module)s]: %(message)s'
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)

    app.logger.handlers.clear()
    app.logger.addHandler(console)
    app.logger.setLevel(logging.INFO)

    # Show werkzeug INFO lines (so "Running on http://..." appears)
    logging.getLogger('werkzeug').setLevel(logging.INFO)

    return app.logger