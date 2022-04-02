

class Coordinate:
    def __init__(self):
        self.x = 0
        self.y = 0

def exit(run_obj):
    run_time = str(datetime.timedelta(seconds=round(time.time() - run_obj.start_time)))
    Logger.info("Exiting shopping mall...")
    print(
        "STATS \truns \t\ttime \t\tias_gloves_seen \tgloves_bought \tclaws_evaluated \tclaws_bought\n"
        f"\t{run_obj.run_count} \t\t{run_time}"
        f"\t\t{run_obj.ias_gloves_seen} \t\t\t{run_obj.gloves_bought} \t\t{run_obj.claws_evaluated} \t\t\t{run_obj.claws_bought}"
    )
    os._exit(0)


def wait_for_loading_screen(timeout):
    start = time.time()
    while time.time() - start < timeout:
        img = grab()
        is_loading_black_roi = np.average(img[:700, 0:250]) < 4.0
        if is_loading_black_roi:
            return True
    return False


