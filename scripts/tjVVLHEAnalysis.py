import ROOT
import argparse
from array import array
from collections import defaultdict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='input.lhe')
    parser.add_argument('-o', '--output', default='output.root')
    args = parser.parse_args()

    binning = {
        'toppt': (60, 0, 1000)}

    hists = {
        'toppt': ROOT.TH1D('toppt', 'toppt', *(binning['toppt']))
    }


    ROOT.gROOT.ProcessLine('#include "LHEF.h"')

    # // Create Reader and Writer object
    reader = ROOT.LHEF.Reader(args.input)
    neve = 0
    # // Read each event and write them out again.
    sumweights = 0.
    sumselected = 0.

    reader.heprup.weightgroup.clear()
    reader.heprup.weightinfo.clear()

    weightgroup = ROOT.LHEF.WeightGroup()
    reader.heprup.weightgroup.push_back(weightgroup)

    while reader.readEvent():
        neve += 1

        real_events = []
        if reader.hepeup.isGroup:
            real_events = reader.hepeup.subevents
        else:
            real_events.append(reader.hepeup)


        #incl_weights = []
        # print '-- Event --'
        for evt in real_events:
            sumweights += evt.XWGTUP

            ###Need this later to use the reweighting
            #for iorig in xrange(1, reader.hepeup.weights.size()):
            #    incl_weights.append(reader.hepeup.weights[iorig].first)

            parts = []
            topquark = None

            for ip in xrange(evt.NUP):
                part = ROOT.Math.PxPyPzEVector(evt.PUP[ip][0], evt.PUP[ip][1], evt.PUP[ip][2], evt.PUP[ip][3])
                part.pdgid = evt.IDUP[ip]
                part.status = evt.ISTUP[ip]
                parts.append(part)
                if part.pdgid in [6,-6]:
                    topquark = part

            

            hists['toppt'].Fill(topquark.pt(), evt.XWGTUP)

        if neve % 5000 == 0:
            print '>> Done %i events' % neve

print '==> Sum of weights/nevents =/%f' % float(sumweights/neve)

outf = ROOT.TFile(args.output, 'RECREATE')

for h in hists.values():
    h.Scale(1./neve) #Scale by the number of events so the integral represents the cross section
    h.Write()

outf.Close()
