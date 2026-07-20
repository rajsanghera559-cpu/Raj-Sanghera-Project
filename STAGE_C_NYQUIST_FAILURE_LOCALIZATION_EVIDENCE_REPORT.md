# Stage C Nyquist Failure-Localization Evidence Report

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Evidence-generation checkpoint: `d7e42477e2bc69b2f36c0ebc506b08ea60be12f0`
- Focused runner: `run_stage_c_nyquist_failure_localization.py`
- Focused runner SHA-256: `945CD7D940CBAA823A15AC6A3E5885F97ED4E46AFE4919C40181F3FCA6B9BFA0`
- Localization design: `STAGE_C_NYQUIST_IMAGINARY_RATIO_FAILURE_LOCALIZATION_AND_REMEDIATION_DESIGN.md`
- Localization design SHA-256: `809196A724D4CD94C936A6A96BB7A6B39717A6667EB57D932ED023C6469EC1A2`
- Protected solver: `project/solver/spectral_solver.py`
- Protected solver SHA-256: `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1`
- Evidence directory: `experiments/advection_form_shadow_audit_localization/stage_c_nyquist_failure_localization_20260720T215450Z_d7e4247`
- Evidence inventory SHA-256: `9FF4E524A0A05ED2E2CC5214E5EE4075254D11852F8CECF895C1F22F87328D5C`
- Run ID: `stage_c_nyquist_failure_localization_20260720T215450Z_d7e4247`
- Created UTC: `2026-07-20T21:54:50+00:00`
- Completed UTC: `2026-07-20T21:54:58+00:00`
- Report type: tracked evidence archive

### Claim boundaries

- Full Stage C operator-form-specificity classification: **not produced**
- Full Stage C rerun: **not performed and not authorized**
- Protected baseline update modification: **not authorized**
- Method superiority: **not authorized**
- Formal convergence: **not established**
- Physical validation: **not established**
- Turbulence, cascade, inertial range, or `k^-3`: **not established**

---

## 1. Archived decision

> **FAILURE CONSISTENT WITH NYQUIST DERIVATIVE CONVENTION**

> **NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT**

The focused diagnostic reproduced the original Stage C integrity failure at the first failing evaluation, compared the existing raw-`ik` derivative route with a Nyquist-zeroed real-compatible diagnostic route, and stopped.

This report archives that localized implementation result. It does not convert the incomplete Stage C trajectory into a completed operator-form-specificity result.

---

## 2. Exact failure location

| Field | Value |
|---|---:|
| Loop index | `3059` |
| Completed steps | `3060` |
| Physical time | `15.3` |
| RK2 stage | `2` |
| Failing quantity | `omega_gradient_imaginary_ratio` |
| Raw imaginary ratio | `1.0021037272233111e-13` |
| Historical threshold | `1e-13` |
| Amount above threshold | `2.1037272233110508e-16` |
| Relative amount above threshold | `0.0021037272233110915` |
| Nyquist-zeroed ratio | `7.983551748537457e-16` |
| Raw real RMS | `0.17710658378815938` |
| Raw imaginary RMS | `1.7747916772990216e-14` |
| Ratio denominator | `0.17710658378815938` |
| Denominator used residual floor | `False` |
| Current-state SHA-256 | `7534D7C24F2666993BBD5B7B79E03B82B8F7F15665B41C30453351A18196E852` |
| Stage-state SHA-256 | `01F5C093F544119D75C4903FBEBC8B809224CABEF12CE125FB94C6AA509BD2B7` |
| Forcing SHA-256 | `504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB` |

---

## 3. Five failing-stage imaginary-ratio measurements

All five parent-gate quantities were recorded separately at the first failing stage.

| Quantity | Direction | Raw real RMS | Raw imaginary RMS | Raw ratio | Raw pass | Nyquist-zeroed real RMS | Nyquist-zeroed imaginary RMS | Nyquist-zeroed ratio |
|---|---|---:|---:|---:|---|---:|---:|---:|
| `omega_gradient_imaginary_ratio` | `x` | `0.17710658378815938` | `1.7747916772990216e-14` | `1.0021037272233111e-13` | `False` | `0.17710658378815938` | `1.4139395766794555e-16` | `7.983551748537457e-16` |
| `projected_baseline_transport_imaginary_ratio` | `projection` | `0.0011197938348772149` | `1.8037511590075336e-19` | `1.6107886137856032e-16` | `True` | `0.0011197938348772149` | `1.8037511590075336e-19` | `1.6107886137856032e-16` |
| `projected_pseudo_transport_imaginary_ratio` | `projection` | `0.0011602939892398818` | `1.7239651574963623e-19` | `1.485800300168534e-16` | `True` | `0.0011602939892398818` | `1.71167382004706e-19` | `1.4752070043630854e-16` |
| `u_x_gradient_imaginary_ratio` | `x` | `0.03390504873353298` | `1.439318302526815e-16` | `4.2451444734344e-15` | `True` | `0.03390504873353298` | `2.937583351123739e-17` | `8.664147260813084e-16` |
| `v_y_gradient_imaginary_ratio` | `y` | `0.04555648477205095` | `1.176601710879505e-16` | `2.582731562294187e-15` | `True` | `0.04555648477205095` | `4.753238276975191e-17` | `1.0433724859937653e-15` |

---

## 4. Nyquist spectral-content measurements

The table below records the full focused bundle's spectral power and Hermitian-symmetry measurements for both RK2 stages.

| Stage | Field | Total power | x-Nyquist power | y-Nyquist power | Corner power | x fraction | y fraction | Corner fraction | Input Hermitian residual | Raw x-derivative residual | Raw y-derivative residual | Zeroed x-derivative residual | Zeroed y-derivative residual |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `1` | `centered_transport` | `21.01329883229191` | `2.0631346280221607e-19` | `7.593680197290141e-20` | `4.306301302824965e-32` | `9.818232941377419e-21` | `3.6137496819969335e-21` | `2.0493218781085973e-33` | `2.234704274774353e-16` | `1.6801139974714438e-09` | `1.0791915784729291e-09` | `7.406904932668547e-16` | `1.0666970740116136e-15` |
| `1` | `pseudo_raw_transport` | `22.56077624094859` | `4.657848033146629e-20` | `1.5383608561118343e-20` | `6.522089640088951e-32` | `2.0645779131892073e-21` | `6.818740807861282e-22` | `2.890897711334565e-33` | `2.3905030344039315e-16` | `7.716841172205652e-10` | `4.675022182018416e-10` | `7.420578943320931e-16` | `1.0450193508029053e-15` |
| `1` | `u_velocity` | `3466.1877564811116` | `1.2198350660245702e-28` | `2.0499820886143295e-29` | `3.397178673876411e-34` | `3.519241171352333e-32` | `5.914226904706051e-33` | `9.800907834621288e-38` | `2.4396455473114244e-16` | `6.0105506794485765e-15` | `2.862148891979198e-15` | `1.3109408252746658e-15` | `1.967083742944399e-15` |
| `1` | `v_velocity` | `5092.80021909768` | `1.5716430940550514e-30` | `6.117007425486916e-29` | `1.1754943508222875e-34` | `3.086009712616428e-34` | `1.201108852169092e-32` | `2.3081493485926616e-38` | `2.100701780515421e-16` | `1.106853605912386e-15` | `4.6065981694579026e-15` | `1.0198688728573512e-15` | `2.013840820645638e-15` |
| `1` | `vorticity` | `83115.55046774243` | `2.985244376873686e-29` | `3.5153807632246935e-29` | `1.5384117747177573e-32` | `3.5916797278895176e-34` | `4.229510294332985e-34` | `1.8509313432446347e-37` | `2.5178119244127034e-16` | `1.1821139335991137e-15` | `2.308500546957609e-15` | `1.0793054073783579e-15` | `2.2430587847274884e-15` |
| `2` | `centered_transport` | `21.03759257999083` | `2.1131211280040069e-19` | `7.91827780542533e-20` | `9.010167137788711e-33` | `1.0044500671687254e-20` | `3.763870687826003e-21` | `4.282888882617879e-34` | `2.6536398826045413e-16` | `1.6993476327356134e-09` | `1.1013656169436731e-09` | `7.384153401964082e-16` | `1.088316036321749e-15` |
| `2` | `pseudo_raw_transport` | `22.58686628614136` | `4.835991869071022e-20` | `1.6581408405419332e-20` | `1.1637687946728352e-32` | `2.141063664080858e-21` | `7.34117260684064e-22` | `5.152413707725758e-34` | `2.4298973642096803e-16` | `7.858398603974967e-10` | `4.850747798062401e-10` | `7.180059302775029e-16` | `1.149656397499334e-15` |
| `2` | `u_velocity` | `3468.2856985546505` | `3.324167813205596e-28` | `4.7719607841397917e-29` | `1.1754943508222875e-36` | `9.584469395329476e-32` | `1.375884572060608e-32` | `3.389266205238383e-40` | `2.335834480377968e-16` | `9.78387038631998e-15` | `3.6023960907853704e-15` | `1.4196128002506782e-15` | `1.7029482800801896e-15` |
| `2` | `v_velocity` | `5095.886972472009` | `1.4210955577147317e-30` | `1.9019724215850152e-28` | `2.618813334535925e-33` | `2.7887109062494762e-34` | `3.732367754346739e-32` | `5.1390726456115676e-37` | `2.7040824176091825e-16` | `1.2319134348951437e-15` | `7.996508108176027e-15` | `1.1620838816934322e-15` | `3.230895435246873e-15` |
| `2` | `vorticity` | `83165.40348096091` | `5.160618834325219e-24` | `1.8983487073139713e-24` | `2.875372029568994e-32` | `6.205247156056474e-29` | `2.282618285797845e-29` | `3.457413671091314e-37` | `2.284196778674123e-16` | `2.0042091994290213e-13` | `1.4394243398084521e-13` | `1.124815436446366e-15` | `1.8890355552725523e-15` |

### Relevant localized Nyquist context

| Field | Value |
|---|---:|
| Relevant field | `vorticity` |
| Relevant derivative direction | `x` |
| Relevant Nyquist-line power fraction | `6.205247156056474e-29` |
| Raw derivative Hermitian residual | `2.0042091994290213e-13` |
| Nyquist-zeroed Hermitian residual | `1.124815436446366e-15` |

---

## 5. Raw-versus-Nyquist-zeroed real-work comparison

The following rows archive the pseudo-spectral operator-work comparisons at stage 1, stage 2, and the stage-weighted level.

| Stage | Operator | Raw work | Nyquist-zeroed work | Absolute difference | Relative difference | Sign changed | Material real-work change | Transport relative difference | Transport cosine similarity |
|---|---|---:|---:|---:|---:|---|---|---:|---:|
| `1` | `SHADOW_PS_ADVECTIVE_PROJECTED_V1` | `8.470329472543003e-22` | `1.0587911840678754e-21` | `2.117582368135751e-22` | `0.2` | `False` | `False` | `3.581560085866813e-16` | `1.0` |
| `1` | `SHADOW_PS_ADVECTIVE_RAW_V1` | `1.0587911840678754e-21` | `1.4823076576950256e-21` | `4.235164736271502e-22` | `0.2857142857142857` | `False` | `False` | `5.305126715227565e-16` | `0.9999999999999999` |
| `2` | `SHADOW_PS_ADVECTIVE_PROJECTED_V1` | `-2.8354427909337704e-19` | `-2.829090043829363e-19` | `6.352747104407253e-22` | `0.0022404779686333084` | `False` | `False` | `3.755608831459645e-16` | `0.9999999999999999` |
| `2` | `SHADOW_PS_ADVECTIVE_RAW_V1` | `-4.235164736271502e-22` | `0.0` | `4.235164736271502e-22` | `1.0` | `False` | `False` | `5.077731589965403e-16` | `0.9999999999999999` |
| `stage_weighted` | `SHADOW_PS_ADVECTIVE_PROJECTED_V1` | `-1.4134862307306137e-19` | `-1.4092510659943422e-19` | `4.235164736271502e-22` | `0.00299625468164794` | `False` | `False` | `2.65325492253609e-16` | `1.0` |
| `stage_weighted` | `SHADOW_PS_ADVECTIVE_RAW_V1` | `3.1763735522036263e-22` | `7.411538288475128e-22` | `4.235164736271502e-22` | `0.5714285714285714` | `False` | `False` | `3.2777283680881894e-16` | `1.0` |

### Real derivative comparison

| Stage | Field | Direction | Raw real RMS | Raw imaginary ratio | Zeroed real RMS | Zeroed imaginary ratio | Real-part relative difference | Real-part maximum difference | Cosine similarity | Removed power fraction | Material change |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `1` | `u_velocity` | `x` | `0.02941981236712881` | `3.0059507306783456e-15` | `0.02941981236712881` | `6.679768858559418e-16` | `1.5614813688553033e-16` | `2.7755575615628914e-17` | `0.9999999999999999` | `0.0` | `False` |
| `1` | `u_velocity` | `y` | `0.03389501241751941` | `1.4336076992157976e-15` | `0.03389501241751941` | `9.87224178302685e-16` | `1.2196732985527016e-16` | `2.7755575615628914e-17` | `1.0` | `0.0` | `False` |
| `1` | `v_velocity` | `x` | `0.04554283505276568` | `5.790641181270861e-16` | `0.04554283505276568` | `5.338942611210197e-16` | `1.4976817356006527e-16` | `5.551115123125783e-17` | `1.0` | `0.0` | `False` |
| `1` | `v_velocity` | `y` | `0.02941981236712881` | `2.302496846562919e-15` | `0.029419812367128814` | `1.0050839603951669e-15` | `1.693427254563215e-16` | `1.734723475976807e-17` | `0.9999999999999999` | `0.0` | `False` |
| `1` | `vorticity` | `x` | `0.17705363711238` | `6.021736473348112e-16` | `0.17705363711238` | `5.49730943277483e-16` | `1.4650312544966873e-16` | `1.1102230246251565e-16` | `1.0` | `0.0` | `False` |
| `1` | `vorticity` | `y` | `0.14952950769636442` | `1.160211256898369e-15` | `0.14952950769636442` | `1.1276633561234433e-15` | `1.6852430465618687e-16` | `1.1102230246251565e-16` | `1.0000000000000002` | `0.0` | `False` |
| `2` | `u_velocity` | `x` | `0.02942871256781585` | `4.8908639792176914e-15` | `0.029428712567815853` | `7.139838088981972e-16` | `1.6188226240380292e-16` | `2.7755575615628914e-17` | `0.9999999999999999` | `0.0` | `False` |
| `2` | `u_velocity` | `y` | `0.03390504873353298` | `1.8083087858935927e-15` | `0.03390504873353298` | `8.664147260813084e-16` | `1.4198267792846731e-16` | `2.7755575615628914e-17` | `1.0000000000000002` | `0.0` | `False` |
| `2` | `v_velocity` | `x` | `0.04555648477205095` | `6.427885478140219e-16` | `0.04555648477205095` | `6.126475929928141e-16` | `1.4670156033530408e-16` | `4.163336342344337e-17` | `1.0` | `0.0` | `False` |
| `2` | `v_velocity` | `y` | `0.029428712567815853` | `3.9981419784101364e-15` | `0.029428712567815853` | `1.6151703089361372e-15` | `1.8825824193766287e-16` | `2.0816681711721685e-17` | `1.0` | `0.0` | `False` |
| `2` | `vorticity` | `x` | `0.17710658378815938` | `1.0021037272233111e-13` | `0.17710658378815938` | `5.74128326744996e-16` | `1.6131742851859297e-16` | `1.6653345369377348e-16` | `1.0` | `0.0` | `False` |
| `2` | `vorticity` | `y` | `0.14957387703253314` | `7.197122741578471e-14` | `0.14957387703253314` | `9.453118450435807e-16` | `1.6478858794014607e-16` | `1.1102230246251565e-16` | `1.0` | `0.0` | `False` |

### Frozen real-work interpretation

- Any material real-work change: `False`
- Frozen effect conclusion: **NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT**

---

## 6. Baseline reproduction and preservation controls

| Control | Result |
|---|---:|
| Last known passing loop reproduced | `3058` |
| Preserved partial rows compared | `3059` |
| Last passing shadow values reproduced | `True` |
| First failing loop reproduced | `3059` |
| Preserved partial evidence modified | `False` |
| Full Stage C rerun performed | `False` |
| Full Stage C rerun authorized | `False` |
| Stage C specificity classification produced | `False` |

---

## 7. Evidence-file inventory

The hashes below were recomputed directly from the seven completed evidence files when this report was generated.

| Evidence file | Bytes | SHA-256 |
|---|---:|---|
| `file_inventory.csv` | `716` | `9FF4E524A0A05ED2E2CC5214E5EE4075254D11852F8CECF895C1F22F87328D5C` |
| `imaginary_ratio_trace.csv` | `8713661` | `A7C1A695DD6F5CC46E7E19577410AB6B9DAC0384DDABC55D8E44E9878AF08ECA` |
| `localization_summary.json` | `15190` | `523D17FC9D48E65FDC2723F228BB28617B88512697E7C4C934318B6F8D6AFA04` |
| `nyquist_spectral_content.csv` | `3272` | `69EAEF8B47287FE4E0A4B8CEB335711ED1CCAFDAA36643872D0C48B6571322A4` |
| `raw_vs_nyquist_zeroed.csv` | `5394` | `9159965240FDCD18979AADF313BBED27DAFE10AFFDA9BCFE50AD2903B5691BE2` |
| `run_metadata.json` | `3949` | `902CE05900F45C7D08FA5AD555E33F55D1E16598A73D38069D3B6BB6C2599F26` |
| `STAGE_C_NYQUIST_FAILURE_LOCALIZATION_REPORT.md` | `1749` | `D76643FCE4703DCDAA6B032DA896D89A589DD226C3A4BBADFD78C02C8DC31CF7` |

---

## 8. Interpretation boundary

The localized result supports a narrow implementation-level statement: the original Stage C `imaginary_ratio` stop at loop index 3059, stage 2, is consistent with the even-grid Nyquist derivative convention, and the diagnostic Nyquist-zeroed route did not materially change real shadow work under the frozen thresholds.

The result does **not** establish the long-time behavior of the complete seven-operator shadow set. The original Stage C run ended after 3,059 completed rows, before the planned 20,001-step comparison and before the final-window classification.

Therefore this evidence must not be described as a completed Stage C operator-form-specificity result.

---

## 9. Authorized next step

The next permitted activity is a design-only shadow-diagnostic Nyquist remediation.

That design must:

- leave the protected baseline solver and accepted update unchanged;
- limit any Nyquist treatment to shadow spectral derivatives and associated diagnostics;
- preserve the historical raw-route failure evidence;
- require exact raw-route reproduction before evaluating a remediated shadow route;
- authorize no full Stage C rerun until the remediation design, implementation, and static inspection are separately archived;
- produce no method-superiority claim.

---

## 10. Final archived statement

> **FAILURE CONSISTENT WITH NYQUIST DERIVATIVE CONVENTION**

> **NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT**

> **This is a focused Nyquist failure-localization result, not a completed Stage C operator-form-specificity result.**
