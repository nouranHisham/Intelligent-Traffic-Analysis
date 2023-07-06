
def parse(cmd):
    
    cmd.add_argument('-i', type=int, help='number of iterations', default=2000)    
    cmd.add_argument('-s', help='which scenario to run.', default="lust")
    cmd.add_argument('-re', type=int, help='Reward function', default=2)    
    cmd.add_argument('--fulldqn', dest='fulldqn', action='store_true', help='use full dqn if true')
    cmd.set_defaults(fulldqn=False)
    cmd.add_argument('-t', type=int, nargs='+', default=[4])
    
    arguments = cmd.parse_args()    
    print("arguments: ",arguments)
    return arguments

