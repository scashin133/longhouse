

/**
 * <p>Abstract superclass CommandProcessingStrategy for the NOTICE and
 * PRIVMSG commands, which share a lot of functionality.
 *
 * @version $Id: MessageStrategy.java,v 1.5 2004/07/26 05:21:39 halcy0n Exp $
 */
public abstract class MessageStrategy implements CommandProcessingStrategy {
    private Chat currentSession;

    public abstract String decorateChannelMessage(String source, String message);

    public abstract String decoratePrivateMessage(String source, String message);

    public void doAction(String source, String target, String message) {
        String action = source + message.substring(7).replace('\001', ' ');
        if (getSession().isCurrentChannel(target)) {
            getSession().sendToUser("* " + action);
        } else {
            if (!getSession().denyPrivateMessagesFrom(source))
                getSession().sendToUser("*> *" + action);
        }
    }

    public abstract void doPing(String source, String message);

    public abstract void doVersion(String source, String message);

    /**
     * Performs the work of command processing. It does not have to be reentrant,
     * the framework guarantees that only one thread will enter this method
     * at a time.
     */	
    public void execute(Command command, Chat session) {
        this.currentSession = session;
        command.stripColoursFromLastArgument();

        try {
          if (command.getArgument(1).startsWith("\001PING")) {
              doPing(command.getSource(), command.getArgument(1));
          } else if (command.getArgument(1).startsWith("\001VERSION")) {
              doVersion(command.getSource(), command.getArgument(1));
          } else if (command.getArgument(1).startsWith("\001ACTION")) {
              doAction(command.getSource(), command.getArgument(0), command.getArgument(1));
          } else {
              if (session.isCurrentChannel(command.getArgument(0)) && !session.isIgnored(command.getFullSource())) {
                  session.sendToUser(decorateChannelMessage(command.getSource(), command.getArgument(1)));
              } else {
                  if (!session.denyPrivateMessagesFrom(command.getSource()) && !session.isIgnored(command.getFullSource()))
                      session.sendToUser(decoratePrivateMessage(command.getSource(), command.getArgument(1)));
              }
          }
        }
        catch (NullPointerException e) {
          System.out.println("NullPointerException caught in MessageStrategy.java");
        }
    }

    protected Chat getSession() {
        return currentSession;
    }
}
