import pysikuli as sik

from pysikuli import Key

if __name__ == "__main__":
    pic_2 = "pics/pic_2.png"
    pic_plus = "pics/pic_plus.png"
    pic_equal = "pics/pic_equal.png"

    sik.tap(Key.win), sik.sleep(1)
    sik.paste("calculator"), sik.sleep(1)
    sik.tap(Key.enter)

    sik.click(pic_2, precision=0.9)
    sik.click(pic_plus)
    sik.click(pic_2, precision=0.9)
    sik.click(pic_equal)
