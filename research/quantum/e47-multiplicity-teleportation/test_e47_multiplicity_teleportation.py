"""Unit tests, runnable with python -m unittest discover -p 'test_*.py'."""
import unittest
from e47_multiplicity_teleportation import run

class Certificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=run()
    def test_full_certificate(self):
        self.assertEqual(self.r['status'],'PASS')
    def test_carrier(self):
        self.assertEqual(self.r['carrier_dimension'],125)
        self.assertEqual(self.r['casimir_sector_dimensions'],[1,9,25,28,27,22,13])
        self.assertEqual((self.r['rank_P47'],self.r['rank_P2'],self.r['selected_E47_complement_rank']),(47,25,78))
    def test_teleportation_ququint(self):
        t=self.r['logical_ququint_teleportation']
        self.assertEqual(t['branches_per_state'],25)
        self.assertEqual(t['input_states'],19)
        self.assertLess(t['max_corrected_channel_error'],5e-10)
        self.assertLess(t['max_no_message_depolarization_error'],5e-10)
    def test_collective_rotation_invariance(self):
        self.assertLess(self.r['max_collective_rotation_intertwiner_error'],5e-10)
        self.assertLess(self.r['max_logical_state_error_after_collective_rotation'],5e-10)
        self.assertLess(self.r['max_encoded_state_sector_leakage'],5e-10)
if __name__=='__main__':unittest.main()