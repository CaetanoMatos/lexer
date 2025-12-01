declare double @llvm.pow.f64(double, double)
define double @calc(double %x) {
entry:
  %t1 = call double @llvm.pow.f64(double %x, double 4)
  %t2 = fmul double 0.25, %t1
  %t3 = call double @llvm.pow.f64(double %x, double 2)
  %t4 = fmul double 1.5, %t3
  %t5 = fadd double %t2, %t4
  ret double %t5
}