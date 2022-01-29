from transmute import SimpleGemPicking, InventoryCollection, Stash


def _create_stash(items: 'list[(int, str, (int, int))]') -> Stash:
    s = Stash()
    s.add_tab(0, InventoryCollection())
    s.add_tab(1, InventoryCollection())
    s.add_tab(2, InventoryCollection())
    s.add_tab(3, InventoryCollection())
    for (tab, item, (x, y)) in items:
        s.append(tab, item, x, y)
    return s


class TestGemPicking:

    def test_first_batch_on_current_page(self):
        subject = SimpleGemPicking(_create_stash([
            (0, "Gem1", (0, 1)),
            (0, "Gem2", (0, 4)),
            (0, "Gem1", (0, 9)),
            (0, "Gem2", (1, 9)),
            (0, "Gem2", (1, 3))
        ]))

        assert(sorted(subject.next_batch()) == sorted([
               (0, "Gem2", 0, 4), (0, "Gem2", 1, 9), (0, "Gem2", 1, 3)
               ]))

        assert(subject.next_batch() == None)

    def test_remaining_picked_up(self):
        subject = SimpleGemPicking(_create_stash([
            (0, "Gem1", (0, 1)),
            (0, "Gem2", (0, 4)),
            (0, "Gem1", (0, 9)),
            (0, "Gem2", (1, 9)),
            (2, "Gem1", (1, 3))
        ]))

        assert(sorted(subject.next_batch()) == sorted([
            (0, "Gem1", 0, 1), (0, "Gem1", 0, 9), (2, "Gem1", 1, 3)
        ]))

    def test_following_tabs(self):
        subject = SimpleGemPicking(_create_stash([
            (0, "Gem1", (0, 1)),
            (1, "Gem3", (1, 3)),
            (1, "Gem3", (2, 3)),
            (1, "Gem2", (0, 4)),
            (2, "Gem1", (0, 9)),
            (1, "Gem2", (1, 9)),
            (1, "Gem2", (1, 3)),
            (2, "Gem3", (1, 3)),
        ]))

        assert(sorted(subject.next_batch()) == sorted([
            (1, "Gem2", 0, 4), (1, "Gem2", 1, 9), (1, "Gem2", 1, 3)
        ]))
        assert(sorted(subject.next_batch()) == sorted([
            (1, "Gem3", 1, 3), (1, "Gem3", 2, 3), (2, "Gem3", 1, 3)
        ]))

    def test_two_gems_notcubable(self):
        subject = SimpleGemPicking(_create_stash([
            (0, "Gem1", (9, 3)),
            (0, "Gem1", (9, 5)),
            (0, "Gem1", (6, 8)),
            (2, "Gem1", (6, 1)),
            (3, "Gem1", (8, 0)),
        ]))

        assert(len(subject.next_batch()) == 3)
        assert(subject.next_batch() is None)

    def test_match_on_first_and_last(self):
        subject = SimpleGemPicking(_create_stash([
            (0, "Gem1", (1, 7)),
            (0, "Gem1", (2, 5)),
            (3, "Gem1", (9, 1)),
            (3, "Gem1", (7, 8)),
        ]))
        assert(len(subject.next_batch()) == 3)
