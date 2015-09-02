#!/usr/local/bin/env python
from __future__ import division
import os
import pandas as pd
import numpy as np
from numpy import array
from scipy import optimize
import matplotlib.pyplot as plt
import seaborn as sns
from radd.toolbox import analyze, colors, messages
from scipy.stats.mstats import mquantiles as mq
import prettyplotlib as pl


sns.set(font='Helvetica', style='white', rc={'text.color': 'black', 'axes.labelcolor': 'black', 'figure.facecolor': 'white'})

cdict = colors.get_cpals('all')
rpal = cdict['rpal']; bpal = cdict['bpal'];
gpal = cdict['gpal']; ppal = cdict['ppal'];
heat = cdict['heat']; cool = cdict['cool'];
slate = cdict['slate']

def react_fit_plots(m, color="#4168B7", is_flat=False, save=False):

      #redata = m.data
      sns.set_context('notebook', font_scale=1.6)
      if is_flat:
            f, axes = plt.subplots(1,3,figsize=(12, 4))
            axes=array([axes])
            fits=[m.fits[0]]
            y=[m.flat_y]
            ncond=1
      else:
            f, axes = plt.subplots(2,3,figsize=(12, 7))
            fits=m.fits.reshape(2,16)
            y=m.avg_y
            ncond=m.ncond

      labels=['Baseline', 'Caution']
      #datas=[redata.query('Cond=="bsl"'), redata.query('Cond=="pnl"')]

      for i in range(ncond):
            plot_fits(y[i], fits[i], kind='radd', colors=[color]*2, axes=axes[i])# data=datas[i], axes=axes[i])

      for ax in axes.flatten():
            if ax.is_last_col():
                  continue
            ax.set_xlim(.4, .65)
            if ax.is_first_col():
                  ax.set_ylabel('P(RT)')
            if ax.is_last_row():
                  ax.set_xlabel('RT (ms)')
            ax.set_xticklabels([int(xx) for xx in ax.get_xticks()*1000])
            #ax.set_ylim(0,11)
      if save:
            kind=m.kind
            mdescr = messages.describe_model(m.depends_on)
            if 'and' in mdescr:
                  mdeps = mdescr.split(' and ')
                  mdescr = '_'.join([dep for dep in mdeps])

            savestr = '_'.join([kind, mdescr, 'fits'])
            plt.savefig(savestr+'.png', dpi=500)
            plt.savefig(savestr+'.svg', rasterized=True)


def scurves(lines=[], kind='pro', yerr=[], pstop=.5, ax=None, linestyles=None, colors=None, markers=False, labels=None, mc=None):
      dont_label=False
      sns.set_context('notebook', font_scale=1.8)
      if len(lines[0])==6:
                kind=='pro'
      if ax is None:
            f, ax = plt.subplots(1, figsize=(5.5,5))
      if colors is None:
            colors = slate(len(lines))
      if labels is None:
            labels=['']*len(lines)
            dont_label=True
      if linestyles is None:
            linestyles = ['-']*len(lines)

      lines=[(line) if type(line)==list else line for line in lines]
      pse=[];
      if kind=='radd':
            x=array([400, 350, 300, 250, 200], dtype='float')
            xtls=x.copy()[::-1]; xsim=np.linspace(15, 50, 10000);
            yylabel='P(Stop)'; scale_factor=100; xxlabel='SSD'; xxlim=(18,42)
            markers=False
      else:
            x=array([100, 80, 60, 40, 20, 0], dtype='float')
            xtls=x.copy()[::-1]; xsim=np.linspace(-5, 11, 10000); xxlim=(-1, 10.5)
            yylabel='P(NoGo)'; scale_factor=100; xxlabel='P(Go)';
            mclinealpha=[.6, .8]*len(lines);
            #if mc is not None:
      markers=False;
      mclinealpha=[.7, 1]*len(lines);            #datamc=heat(len(x));
                  #mc=heat(len(x))


      x=analyze.res(-x, lower=x[-1]/10, upper=x[0]/10)
      for i, yi in enumerate(lines):
            if i == 0:
                  color='k'
            else:
                  color = colors[i]
            y=analyze.res(yi, lower=yi[-1], upper=yi[0])
            p_guess=(np.mean(x),np.mean(y),.5,.5)
            p, cov, infodict, mesg, ier = optimize.leastsq(analyze.residuals, p_guess, args=(x,y), full_output=1, maxfev=5000, ftol=1.e-20)
            x0,y0,c,k=p
            xp = xsim
            pxp=analyze.sigmoid(p,xp)
            idx = (np.abs(pxp - pstop)).argmin()
            pse.append(xp[idx]/scale_factor)
            # Plot the results
            if i==0 and yerr!=[]:
                  #ax.errorbar(x, y[i], yerr=yerr[i], color=colors[i], marker='o', elinewidth=2, ecolor='k')
                  ax.errorbar(x, y, yerr=yerr, color=color, ecolor=color, capsize=0, lw=0, elinewidth=3)
            if markers:
                  a = mclinealpha[i]
                  ax.plot(xp, pxp, linestyle=linestyles[i], lw=2.5, color=color, label=labels[i], alpha=a)
                  for ii in range(len(y)):
                        if i%2==0:
                              ax.plot(x[ii], y[ii], lw=0, marker='o', ms=9, color='k', markerfacecolor='none', mec='k', mew=1.5, alpha=.8)#mc[ii], alpha=1)
                        else:
                              #color=mc[ii]
                              ax.plot(x[ii], y[ii], lw=0, marker='x', ms=7, color=color, mew=3, alpha=a)
            else:
                  ax.plot(xp, pxp, linestyle=linestyles[i], lw=3.5, color=colors[i], label=labels[i])
            pse.append(xp[idx]/scale_factor)

      plt.setp(ax, xlim=xxlim, xticks=x, ylim=(-.01, 1.05), yticks=[0, 1])
      ax.set_xticklabels([int(xt) for xt in xtls]); ax.set_yticklabels([0.0, 1.0])
      ax.set_xlabel(xxlabel); ax.set_ylabel(yylabel)
      #if dont_label:
      ax.legend(loc=0);
      plt.tight_layout(); sns.despine()
      return (pse)



def plot_fits(y, yhat, cdf=False, plot_params={}, save=False, axes=None, kind='radd', savestr='fit_plot', split='HL', xlim=(.4, .65), label=None, colors=None, data=None, mc=None):
      sns.set_context('notebook', font_scale=1.6)

      pp=plot_params
      if axes is None:
            f, (ax1, ax2, ax3) = plt.subplots(1,3,figsize=(14, 5.5), sharey=False)
      else:
            ax1, ax2, ax3 = axes
      if colors is None:
            colors=["#4168B7"]*2
      if kind=='pro':
            xlim=(.48, .58)
      # pull out data vectors
      sc, gq, eq = unpack_yvector(y, kind=kind)
      fitsc, fitgq, fiteq = unpack_yvector(yhat, kind=kind)

      if data is not None:
            axes, pp = plot_data_dists(data, kind=kind, cdf=cdf, axes=[ax1,ax2,ax3], data_type='real')
            fit_cq, fit_eq = [analyze.kde_fit_quantiles(q, bw=.001) for q in [fitgq, fiteq]]
      else:
            kdefits = [analyze.kde_fit_quantiles(q, bw=.001) for q in [gq, fitgq, eq, fiteq]]
            dat_cq, fit_cq, dat_eq, fit_eq = kdefits
            axes, pp = plot_data_dists(data=[dat_cq, dat_eq], kind=kind, cdf=cdf, axes=[ax1,ax2,ax3], data_type='interpolated')
            #ax1, ax2, ax3 = axes

      shade=pp['shade']; lw=pp['lw']; ls=pp['ls']; alpha=pp['alpha']; bw=pp['bw']
      sns.distplot(fit_cq, kde=False, color=colors[0], norm_hist=True, ax=ax1, bins=45)
      sns.distplot(fit_eq, kde=False, color=colors[1], norm_hist=True, ax=ax2, bins=45)
      #sns.kdeplot(fit_cq, color='Blue', cumulative=cdf, linestyle='--', bw=.01, ax=ax1,linewidth=3, alpha=.70, shade=shade, label=label)
      #sns.kdeplot(fit_eq, color='Red', cumulative=cdf, linestyle='--', bw=.01, ax=ax2,linewidth=3, alpha=.60, shade=shade)

      for ax in axes:
            if ax.is_last_col():
                  continue
            ax.set_xlim(xlim[0], xlim[1])
            if ax.is_first_col():
                  ax.set_ylabel('P(RT)')
            if ax.is_last_row():
                  ax.set_xlabel('RT (ms)')
            ax.set_xticklabels([int(xx) for xx in ax.get_xticks()*1000])

      # Plot observed and predicted stop curves
      scurves([sc, fitsc], kind=kind, linestyles=['-','--'], ax=ax3, colors=colors, markers=True, mc=mc)
      plt.tight_layout()
      sns.despine()
      if save:
            plt.savefig(savestr+'.png', format='png', dpi=300)


def profits(y, yhat, cdf=False, plot_params={}, save=False, axes=None, kind='radd', savestr='fit_plot', split='HL', xlim=(.4, .65), label=None, colors=None, data=None, mc=None):
      sns.set_context('notebook', font_scale=1.6)

      pp=plot_params
      if axes is None:
            f, (ax1, ax2, ax3) = plt.subplots(1,3,figsize=(14, 5.5), sharey=False)
      else:
            ax1, ax2, ax3 = axes
      if colors is None:
            colors=["#4168B7"]*2
      if kind=='pro':
            xlim=(.48, .58)
      # pull out data vectors
      sc, gq, eq = unpack_yvector(y, kind=kind)
      fitsc, fitgq, fiteq = unpack_yvector(yhat, kind=kind)
      kdefits = [analyze.kde_fit_quantiles(q, bw=.005) for q in [gq, fitgq, eq, fiteq]]
      dat_cq, fit_cq, dat_eq, fit_eq = kdefits
      #shade=pp['shade']; lw=pp['lw']; ls=pp['ls']; alpha=pp['alpha']; bw=pp['bw']
      sns.distplot(fit_cq, kde=False, color=colors[0], norm_hist=True, ax=ax1, bins=25)
      sns.distplot(fit_eq, kde=False, color=colors[1], norm_hist=True, ax=ax2, bins=25)
      #sns.kdeplot(fit_cq, color='Blue', cumulative=cdf, linestyle='--', bw=.01, ax=ax1,linewidth=3, alpha=.70, shade=shade, label=label)
      #sns.kdeplot(fit_eq, color='Red', cumulative=cdf, linestyle='--', bw=.01, ax=ax2,linewidth=3, alpha=.60, shade=shade)

      for ax in axes:
            if ax.is_last_col():
                  continue
            ax.set_xlim(xlim[0], xlim[1])
            if ax.is_first_col():
                  ax.set_ylabel('P(RT)')
            if ax.is_last_row():
                  ax.set_xlabel('RT (ms)')
            ax.set_xticklabels([int(xx) for xx in ax.get_xticks()*1000])

      # Plot observed and predicted stop curves
      scurves([sc, fitsc], kind=kind, linestyles=['-','--'], ax=ax3, colors=colors, markers=True, mc=mc)
      plt.tight_layout()
      sns.despine()
      if save:
            plt.savefig(savestr+'.png', format='png', dpi=300)


def plot_data_dists(data, kind='radd', data_type='real', cdf=False, axes=[], get_rts=False):

      emp_kq = lambda rts: analyze.kde_fit_quantiles(mq(rts, prob=np.arange(0,1,.02)), bw=.008)

      ax1, ax2, ax3 = axes
      if data_type=='real':
            if kind=='pro':
                  hi_rts = data.query('response==1 & pGo>.5').rt.values
                  lo_rts = data.query('response==1 & pGo<.5').rt.values
            elif kind=='radd':
                  hi_rts = data.query('response==1 & acc==1').rt.values
                  lo_rts = data.query('response==1 & acc==0').rt.values
            dat_cq = emp_kq(hi_rts)
            dat_eq = emp_kq(lo_rts)
            if get_rts:
                  return axes, plot_params, rts
      elif data_type=='interpolated':
            dat_cq, dat_eq = data

      if cdf:
            shade=False; alpha=1; bw=.01; lw=3.5; ls='--'
            sns.kdeplot(dat_cq, color='k', cumulative=cdf, ax=ax1, linewidth=lw, linestyle='-')
            sns.kdeplot(dat_eq, color='k', cumulative=cdf, ax=ax2, linewidth=lw, linestyle='-')
      else:
            # set parameters for simulated plots
            shade=True; alpha=.5; bw=.01; lw=2.5; ls='-'
            sns.distplot(dat_cq, kde=False, color='k', norm_hist=True, ax=ax1, bins=50)
            sns.distplot(dat_eq, kde=False, color='k', norm_hist=True, ax=ax2, bins=50)

      plot_params={'shade':shade, 'alpha':alpha, 'bw':bw, 'lw':lw, 'ls':ls}
      if get_rts:
            return axes, plot_params, rts
      return axes, plot_params



def plot_reactive_fits(model, cumulative=False, plot_sims=False, save=False, col=None):

      sns.set_context('notebook', font_scale=1.6)
      f, (ax1, ax2,ax3) = plt.subplots(1,3,figsize=(14, 6))
      y = model.avg_y; r,c=y.shape
      xlim=(.43, .65)
      if col is None:
            col=[bpal(2), ppal(2)]

      if plot_sims:
            yhat = model.simulator.sim_fx(model.popt).reshape(r, c)
            yh_id='sims.png'
      else:
            yhat = model.fits.reshape(r, c)
            yh_id='fits.png'

      if save:
            savestr = '_'.join([get_model_name(model), yh_id])


      linestyles = ['-', '--']*10
      for i in range(model.ncond):
            gq, eq, sc = unpack_yvector(y[i])
            gqhat, eqhat, sc_hat = unpack_yvector(yhat[i])

            for ii, qc in enumerate([gq, gqhat]):
                  kdeqc = analyze.kde_fit_quantiles(qc, bw='scott')
                  sns.kdeplot(kdeqc, linestyle=linestyles[ii], cumulative=cumulative, ax=ax1, linewidth=3.5, alpha=.7, color=col[ii][i])
            for ii, qe in enumerate([eq, eqhat]):
                  kdeqe = analyze.kde_fit_quantiles(qe, bw='scott')
                  sns.kdeplot(kdeqe, cumulative=cumulative, color=col[ii][i], linestyle=linestyles[ii], ax=ax2, linewidth=3.5, alpha=.7)

            labels = [' '.join([model.labels[i], x]) for x in ['data', 'model']]
            # Plot observed and predicted stop curves
            scurves([sc, sc_hat], labels=labels, kind='radd', colors=col[i], linestyles=['-','--'], ax=ax3, markers=True)
            plt.tight_layout()
            sns.despine()

      ax1.set_title('Correct RTs')
      ax2.set_title('SS Trial RTs (Errors)')
      ax3.set_title('P(Stop) Across SSD')
      for axx in [ax1, ax2]:
            axx.set_xlim(.46, .64)
            axx.set_ylabel('P(RT<t)')
            axx.set_xlabel('RT (s)')
            #axx.set_ylim(-.05, 1.05)
            axx.set_xticklabels(ax1.get_xticks())
      if save:
            plt.savefig(savestr, dpi=300)


def unpack_yvector(y, kind='radd'):

      if 'pro' in kind:
            sc, gq, eq = y[:6], y[6:11], y[11:]
      else:
            sc, gq, eq = y[1:6], y[6:11], y[11:]

      return sc, gq, eq


def get_model_name(model):
      mname=model.kind
      mdep = messages.describe_model(model.depends_on)
      if 'x' in model.kind:
            mname = '_'.join([mname, model.dynamic])
      mname='_'.join([mname, mdep])
      return mname

def plot_idx_fits(obs, sim, kind='radd', save=False):


      if kind=='radd':
            df = df.where(df>0).dropna()
            for idx, idx_c in obs.iterrows():
                  try:
                        save_str = '_'.join([str(idx), idx_c['Cond'], 'pred'])
                        y = idx_c.loc['Go':'e90'].values.astype(np.float)
                        yhat = df.iloc[idx, :].values.astype(np.float)
                        plot_fits(y, yhat, kind='radd', save=save, savestr=save_str)
                  except Exception:
                        continue
      elif kind=='pro':
            """
            FILL THIS IN
            """

            df=None


def plot_kde_cdf(quant, bw=.1, ax=None, color=None):

      if ax is None:
            f, ax = plt.subplots(1, figsize=(5,5))
      if color is None:
            color='k'
      kdefits = analyze.kde_fit_quantiles(quant, bw=bw)
      sns.kdeplot(kdefits, cumulative=True,  color=color, ax=ax, linewidth=2.5)

      ax.set_xlim(kdefits.min()*.94, kdefits.max()*1.05)
      ax.set_ylabel('P(RT<t)')
      ax.set_xlabel('RT (s)')
      ax.set_ylim(-.05, 1.05)
      ax.set_xticklabels(ax.get_xticks()*.1)

      plt.tight_layout()
      sns.despine()


def gen_pro_traces(ptheta, bias_vals=[], bias='v', integrate_exec_ss=False, return_exec_ss=False, pgo=np.arange(0, 1.2, .2)):

      dvglist=[]; dvslist=[]

      if bias_vals==[]:
            deplist=np.ones_like(pgo)

      for val, pg in zip(bias_vals, pgo):
            ptheta[bias] = val
            ptheta['pGo'] = pg
            dvg, dvs = RADD.run(ptheta, ntrials=10, tb=.565)
            dvglist.append(dvg[0])

      if pg<.9:
            dvslist.append(dvs[0])
      else:
            dvslist.append([0])

      if integrate_exec_ss:
            ssn = len(dvslist[0])
            traces=[np.append(dvglist[i][:-ssn],(dvglist[i][-ssn:]+ss)-dvglist[i][-ssn:]) for i, ss in enumerate(dvslist)]
            traces.append(dvglist[-1])
            return traces

      elif return_exec_ss:
            return [dvglist, dvslist]

      else:
            return dvglist


def gen_re_traces(rtheta, integrate_exec_ss=False, ssdlist=np.arange(.2, .45, .05)):

      dvglist=[]; dvslist=[]
      rtheta['pGo']=.5
      rtheta['ssv']=-abs(rtheta['ssv'])
      #animation only works if tr<=ssd
      rtheta['tr']=np.min(ssdlist)-.001

      for ssd in ssdlist:
            rtheta['ssd'] = ssd
            dvg, dvs = RADD.run(rtheta, ntrials=10, tb=.650)
            dvglist.append(dvg[0])
            dvslist.append(dvs[0])

      if integrate_exec_ss:
            ssn = len(dvslist[0])
            traces=[np.append(dvglist[i][:-ssn],(dvglist[i][-ssn:]+ss)-dvglist[i][-ssn:]) for i, ss in enumerate(dvslist)]
            traces.append(dvglist[-1])
            return traces

      ssi, xinit_ss = [], []
      for i, (gtrace, strace) in enumerate(zip(dvglist, dvslist)):
            leng = len(gtrace)
            lens = len(strace)
            xinit_ss.append(leng - lens)
            ssi.append(strace[0])
            dvslist[i] = np.append(gtrace[:leng-lens], strace)
            dvslist[i] = np.append(dvslist[i], ([0]))

      return [dvglist, dvslist, xinit_ss, ssi]


def build_decision_axis(theta, gotraces):

      # init figure, axes, properties
      f, ax = plt.subplots(1, figsize=(7,4))

      w=len(gotraces[0])+50
      h=theta['a']
      start=-100

      plt.setp(ax, xlim=(start-1, w+1), ylim=(0-(.01*h), h+(.01*h)))

      ax.hlines(y=h, xmin=-100, xmax=w, color='k')
      ax.hlines(y=0, xmin=-100, xmax=w, color='k')
      ax.hlines(y=theta['z'], xmin=start, xmax=w, color='Gray', linestyle='--', alpha=.7)
      ax.vlines(x=w-50, ymin=0, ymax=h, color='r', linestyle='--', alpha=.5)
      ax.vlines(x=start, ymin=0, ymax=h, color='k')

      ax.set_xticklabels([])
      ax.set_yticklabels([])
      ax.set_xticks([])
      ax.set_yticks([])

      sns.despine(top=True, right=True, bottom=True, left=True)

      return f, ax


def re_animate(i, x, dvg_traces, dvg_lines, dvs_traces, dvs_lines, rtheta, xi, yi):

      clist=['#2c724f']*len(dvg_traces)
      clist_ss = sns.light_palette('#c0392b', n_colors=6)[::-1]

      for nline, (gl, g) in enumerate(zip(dvg_lines, dvg_traces)):
            if g[i]>=rtheta['a'] or dvs_traces[nline][i]<=0:
                  continue
            gl.set_data(x[:i+1], g[:i+1])
            gl.set_color(clist[nline])

            if dvs_traces[nline][i]>0:
                  ssi = len(g) - len(dvs_traces[nline]) + 1
                  dvs_lines[nline].set_data(x[xi[nline]:i+1], dvs_traces[nline][xi[nline]:i+1])
                  dvs_lines[nline].set_color(clist_ss[nline])

      return dvs_lines, dvg_lines


def pro_animate(i, x, protraces, prolines):

      clist = sns.color_palette('autumn', n_colors=6)[::-1]

      for nline, (pline, ptrace) in enumerate(zip(prolines, protraces)):
            pline.set_data(x[:i+1], ptrace[:i+1])
            pline.set_color(clist[nline])

      return prolines,


def plot_all_traces(DVg, DVs, theta, ssd=np.arange(.2,.45,.05), kind='radd'):

      ncond = DVg.shape[0]
      nssd = DVs.shape[1]
      f, axes = plt.subplots(nssd, ncond, figsize=(12,14))
      for i in range(ncond):
            params = {k:v[i] if hasattr(v, '__iter__') else v for k,v in theta.items()}
            for ii in range(nssd):
                  plot_traces(DVg=DVg[i], DVs=DVs[i, ii], ssd=ssd[ii], sim_theta=params, ax=axes[ii,i], kind=kind)
      return f


def plot_traces(DVg=[], DVs=[], sim_theta={}, kind='radd', ssd=.450, ax=None, tau=.001, tb=.650, cg='#2c724f', cr='#c0392b'):
      if ax is None:
            f,ax=plt.subplots(1,figsize=(8,5))
      tr=sim_theta['tr']; a=sim_theta['a']; z=sim_theta['z'];
      for i, igo in enumerate(DVg):
            ind = np.argmax(igo>=a)
            xx = [np.arange(tr, tr+(len(igo[:ind-1])*tau), tau), np.arange(tr, tb, tau)]
            x = xx[0 if len(xx[0])<len(xx[1]) else 1]
            plt.plot(x, igo[:len(x)], color=cg, alpha=.1, linewidth=.5)
            if kind in ['irace', 'radd', 'iact'] and i<len(DVs):
                  if np.any(DVs<=0):
                        ind=np.argmax(DVs[i]<=0)
                  else:
                        ind=np.argmax(DVs[i]>=a)
                  xx = [np.arange(ssd, ssd+(len(DVs[i, :ind-1])*tau), tau), np.arange(ssd, tb, tau)]
                  x = xx[0 if len(xx[0])<len(xx[1]) else 1]
                  #x = np.arange(ssd, ssd+(len(DVs[i, :ind-1])*tau), tau)
                  plt.plot(x, DVs[i, :len(x)], color=cr, alpha=.1, linewidth=.5)

      xlow = np.min([tr, ssd])
      xlim = (xlow*.95, 1.05*tb)
      if kind=='pro' or np.any(DVs<=0):
            ylow=0
            ylim=(-.03, a*1.03)
      else:
            ylow=z
            ylim=(z-.03, a*1.03)

      plt.setp(ax, xlim=xlim, ylim=ylim)
      ax.hlines(y=z, xmin=xlow, xmax=tb, linewidth=2, linestyle='--', color="k", alpha=.5)
      ax.hlines(y=a, xmin=xlow, xmax=tb, linewidth=2, linestyle='-', color="k")
      ax.hlines(y=ylow, xmin=xlow, xmax=tb, linewidth=2, linestyle='-', color="k")
      ax.vlines(x=xlow, ymin=ylow*.998, ymax=a*1.002, linewidth=2, linestyle='-', color="k")
      sns.despine(top=True,bottom=True, right=True, left=True)
      xlim = (xlow*.95, 1.05*tb)
      ax.set_xticklabels([])
      ax.set_yticklabels([])
      ax.set_xticks([])
      ax.set_yticks([])

      return ax
