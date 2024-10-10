# Press the green button in the gutter to run the script.
from app.picstax import PicStax

if __name__ == '__main__':
    app = PicStax()
    app.setup()
    app.run()
    app.cleanup()
